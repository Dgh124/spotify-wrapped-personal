from django.urls import path
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("auth/", views.auth, name="auth"),

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