import uuid

from django.db import models

from django.contrib.postgres.fields import ArrayField

from spotify_wrapped.Spotify import Artist


class User(models.Model):
    id = models.CharField(max_length=22, default=0, primary_key=True)
    display_name = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.display_name


class Artist(models.Model):
    name = models.CharField(max_length=200)
    id = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    genres = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"



class Track(models.Model):
    album_name = models.CharField(max_length=200)
    album_image = models.CharField(max_length=200)
    track_name = models.CharField(max_length=200)
    artist_list = models.ManyToManyField(Artist, blank=True, related_name='artist_list')



    def __str__(self):
        return f"{self.track_name}"



class Wrap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    top_tracks = models.ManyToManyField(Track)
    top_artists = models.ManyToManyField(Artist)
    top_audio = models.CharField(max_length=300)
    suggested_tracks = models.ManyToManyField(Track)
    personality = ArrayField(models.CharField(max_length=255), default=list)
    color = models.CharField(max_length=255)
    #genres requires a dictionary as input. by default genres is a tuple. use
    #helper function to convert
    top_genres = models.JSONField(blank = True, default=dict)

    def __str__(self):
        return self.id


    #on hold, currently wraps only have one user
    #def get_users(self):
    #    return list(self.users.all())



