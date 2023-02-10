from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Trope(models.Model):
    """This is the model for the bingo elements that are tropes"""
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='tropes')

    def __str__(self):
        return self.name + "-" + self.description


class BingoSheet(models.Model):
    """Model for the bingo sheet"""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)  # we can't save the bingo as bingo in the database so I created a coding
    # system for this (similar to the s one )
    checked = models.CharField(max_length=25)  # witch fields are marked
    private = models.BooleanField(default=False)  # for future use when i have a friend list implemented
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)  # for now is one but in future i thing of makin it
    # multi-genre

    def __str__(self):
        return self.name + "( " + self.code + ")"
