from django.urls import path
from . import views

app_name = "spotify_wrapped"
urlpatterns = [
    path("", views.index, name="index"),
]