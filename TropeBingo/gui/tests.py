from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import FriendRequest, Friends, BingoSheet, Genre
from base.forms import UserForm


class DefaultViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='top_secret')
        self.other_user = User.objects.create_user(username='otheruser', password='top_secret')
        self.friend_request = FriendRequest.objects.create(sender=self.user, receiver=self.other_user)

    def test_default_view_with_logged_in_user(self):
        self.client.login(username='testuser', password='top_secret')
        response = self.client.get('/default')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'default.html')
        self.assertNotContains(response, 'testuser')
        self.assertNotContains(response, 'otheruser')
        self.assertNotContains(response, 'Accept')

    def test_view_with_logged_out_user(self):
        response = self.client.get('/default')
        self.assertRedirects(response, '/login?next=/default')

    def test_default_view_with_request_on_page(self):
        self.client.login(username='otheruser', password='top_secret')
        response = self.client.get('/default')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'default.html')
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Accept')
        self.assertContains(response, 'DELETE')


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass')
        self.friend_user = User.objects.create_user(username='user_friend', password='testpass')
        self.request_user = User.objects.create_user(username='user_request', password='testpass')
        self.friend = Friends.objects.create(owner=self.user)
        self.friend.friends.add(self.friend_user)
        self.friend_request = FriendRequest.objects.create(sender=self.request_user, receiver=self.user)

    def test_search_view_with_query(self):
        self.client.login(username='test_user', password='testpass')
        response = self.client.get('/search', {'q': 'testuser2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertQuerysetEqual(response.context['users'], [self.user2])
        self.assertQuerysetEqual(response.context['friends'], [self.friend_user])
        self.assertQuerysetEqual(response.context['have_fq'], [self.request_user])
        self.assertContains(response, 'testuser2')
        self.assertContains(response, 'Send friend request')
        self.assertNotContains(response, 'user_friend')
        self.assertNotContains(response, 'user_request')

    def test_search_view_without_query(self):
        self.client.login(username='test_user', password='testpass')
        response = self.client.get('/search', {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertQuerysetEqual(response.context['users'].order_by('username'), User.objects.all())
        self.assertQuerysetEqual(response.context['friends'], [self.friend_user])
        self.assertQuerysetEqual(response.context['have_fq'], [self.request_user])
        self.assertContains(response, 'testuser2')
        self.assertContains(response, 'Send friend request')
        self.assertNotContains(response, 'user_friend')
        self.assertNotContains(response, 'user_request')
        self.assertNotContains(response, 'test_user')


class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='top_secret')
        self.genre = Genre.objects.create(name='RomCom')
        self.bingo_sheet = BingoSheet.objects.create(owner=self.user, name='Test Bingo Sheet', genre=self.genre)
        self.friend = User.objects.create_user(username='friend', password='top_secret')
        self.friends_list = Friends.objects.create(owner=self.user)
        self.friends_list.friends.add(self.friend)

    def test_profile_view_with_logged_in_user(self):
        self.client.login(username='testuser', password='top_secret')
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test Bingo Sheet')
        self.assertContains(response, 'friend')

    def test_profile_view_with_logged_out_user(self):
        response = self.client.get('/profile')
        self.assertRedirects(response, '/login?next=/profile')


class EditProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='top_secret')

    def test_user_edit_view_with_logged_in_user(self):
        self.client.login(username='testuser', password='top_secret')
        response = self.client.get(f'/user_edit?id={self.user.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('user/user_edit.html')
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertEqual(response.context['user'], self.user)

    def test_user_edit_view_with_logged_out_user(self):
        response = self.client.get(f'/user_edit?id={self.user.pk}')
        self.assertRedirects(response, f'/login?next=/user_edit?id={self.user.pk}')

    def test_edit_profile(self):
        self.client.login(username='testuser', password='top_secret')
        data = {'email': 'newusername@username.new', 'first_name': 'New', 'last_name': 'Name'}
        response = self.client.post(f'/user_edit?id={self.user.pk}', data)
        self.assertRedirects(response, f'/profile?id={self.user.pk}')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'newusername@username.new')

    def test_user_edit_invalid_link(self):
        self.client.login(username='testuser', password='top_secret')
        response = self.client.get('/user_edit?id=123')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Invalid link. No ID found.', status_code=404)
