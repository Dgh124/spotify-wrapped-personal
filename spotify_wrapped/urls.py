from django.urls import path
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.profile, name="index"),
    path("login/", views.logIn, name="login"),
    path("wrap/", views.wrap, name="wrap"),
    path("wrapped/", views.wrapped, name="wrapped"),
    path("duo_wrap", views.duo_wrap, name="duo_wrap"),
    path("auth/", views.auth, name="auth"),
    path("logout/", views.logout, name="logout"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("delete_wrap/", views.delete_wrap, name="delete_wrap"),

    path("profile/", views.profile, name="profile"),

    path("slideshow/", views.slideshow, name="slideshow"),
    # path("contact-developers/", views.feedback_view, name="contact_devs"),

    # paths for all slides 
    path("meetDevs/", views.meetDevs, name="meetDevs"),
]
