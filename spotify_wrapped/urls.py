from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.profile, name="index"),
    path("login/", views.logIn, name="login"),
    path("auth/", views.auth, name="auth"),
    path("logout/", views.logout, name="logout"),

    path("profile/", views.profile, name="profile"),

    path("slideshow/", views.slideshow, name="slideshow"),
    # path("contact-developers/", views.feedback_view, name="contact_devs"),

    # paths for all pages
    path("cover/", views.cover, name="cover"),
    path("AI_Query/", views.AI_Query, name="AI_Query"),
    path("albums/", views.albums, name="albums"),
    path("artists/", views.artists, name="artists"),
    path("genres/", views.genres, name="genres"),
    path("meetDevs/", views.meetDevs, name="meetDevs"),
    path("mood/", views.mood, name="mood"),
    path("popularityScore/", views.popularityScore, name="popularityScore"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("tracks/", views.tracks, name="tracks"),
]
