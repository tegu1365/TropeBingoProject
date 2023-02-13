from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import FriendRequest, Friends, BingoSheet, Genre


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


class SearchViewTestCase(TestCase):
    pass


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
