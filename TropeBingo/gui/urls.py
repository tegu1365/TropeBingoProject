from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index),
    path('login', auth_views.LoginView.as_view()),
    path('logout', auth_views.LogoutView.as_view()),
    path('default', views.default),
    path('register', views.register),
    path('profile', views.profile),
    path('newbingo', views.create_bingo),
    path('bingo', views.bingo),
    path('play_bingo', views.play_bingo),
    path('bingo_settings', views.bingo_settings),
    path('bingo_delete', views.bingo_delete)
]
