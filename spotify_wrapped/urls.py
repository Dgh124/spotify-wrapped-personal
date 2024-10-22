from django.urls import path
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("auth/", views.auth, name="auth"),
]