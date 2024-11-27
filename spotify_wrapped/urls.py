from django.urls import path
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.profile, name="index"),
    path("login/", views.logIn, name="login"),
    path("wrap/", views.wrap, name="wrap"),
    path("auth/", views.auth, name="auth"),
    path("logout/", views.logout, name="logout"),

    path("profile/", views.profile, name="profile"),

    path("slideshow/", views.slideshow, name="slideshow"),
    # path("contact-developers/", views.feedback_view, name="contact_devs"),

    # paths for all slides 
    path("meetDevs/", views.meetDevs, name="meetDevs"),
]
