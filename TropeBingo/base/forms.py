from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.views.generic import CreateView

from gui.models import BingoSheet, PersonalTrope, Genre, Type


class RegisterUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        email = forms.EmailField(max_length=200, help_text='Required')
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",
                  "password1", "password2")


class UserForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class BingoForm(forms.ModelForm):
    code = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].disabled = True
        self.fields['code'].required = False

    class Meta:
        model = BingoSheet
        fields = ['name', 'private', 'genre', 'type', 'code']


class BingoSettingsForm(forms.ModelForm):
    class Meta:
        model = BingoSheet
        fields = ['name', 'private']


class PersonalTropeForm(forms.ModelForm):
    name = forms.CharField()
    description = forms.CharField()
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    types = forms.ModelMultipleChoiceField(
        queryset=Type.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = PersonalTrope
        fields = ['name', 'description', 'genres', 'types']
