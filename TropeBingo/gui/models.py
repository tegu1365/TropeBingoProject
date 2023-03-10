from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def add_default_type(cls):
        exam, created = cls.objects.get_or_create(
            title='type'
        )

    def __str__(self):
        return self.name



class Trope(models.Model):
    """This is the model for the bingo elements that are tropes"""
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='trope_genres')
    types = models.ManyToManyField(Type, related_name='trope_types', default=None)

    def __str__(self):
        return self.name + "-" + self.description


class BingoSheet(models.Model):
    """Model for the bingo sheet"""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)  # we can't save the bingo as bingo in the database, so I created a coding
    # system for this (similar to the s one )
    checked = models.CharField(max_length=25, default='0' * 25)  # witch fields are marked
    private = models.BooleanField(default=False)  # for future use when i have a friend list implemented
    bingo_done = models.BooleanField(default=False)
    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE)  # for now is one but in future i think of making it multi-genre
    type = models.ForeignKey(Type, on_delete=models.CASCADE, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + "( " + self.code + ")"


class PersonalTrope(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='personal_trope_genres')
    types = models.ManyToManyField(Type, related_name='personal_trope_types', default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + "-" + self.description


class Friends(models.Model):
    friends = models.ManyToManyField(User)
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE, null=True)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, create = cls.objects.get_or_create(
            owner=current_user
        )
        friend.friends.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, remove_friend):
        friend, create = cls.objects.get_or_create(
            owner=current_user
        )
        friend.friends.remove(remove_friend)


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, null=True, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, null=True, related_name='receiver', on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(auto_now_add=True)
