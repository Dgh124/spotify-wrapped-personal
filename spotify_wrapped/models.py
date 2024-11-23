import uuid

from django.db import models


class UserModel(models.Model):
    id = models.TextField(default=0, primary_key=True)
    display_name = models.CharField(max_length=30, default="")
    pfp = models.TextField(default="", blank=True, null=True)
    product = models.TextField(default="")
    uri = models.TextField(default="")

    def __str__(self):
        return self.display_name


class ArtistModel(models.Model):
    name = models.CharField(max_length=200)
    id = models.CharField(max_length=200, primary_key=True)
    image = models.CharField(max_length=200)
    genres = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"



class TrackModel(models.Model):
    track_id = models.TextField(blank=True)
    album_name = models.TextField(blank=True)
    album_image = models.TextField(blank=True)
    track_name = models.TextField(blank=True)
    artist_list = models.JSONField(default = list) #list of strings
    preview_url = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.track_name}"



class WrapModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ManyToManyField(UserModel, related_name="user")
    top_tracks = models.ManyToManyField(TrackModel, related_name='top_tracks')
    top_artists = models.ManyToManyField(ArtistModel)
    top_audio = models.TextField(blank=True)
    suggested_tracks = models.ManyToManyField(TrackModel, related_name='suggested_tracks')
    personality = models.JSONField(default = list) #list of strings
    color = models.TextField(blank = True)
    #genres requires a dictionary as input. by default genres is a tuple. use
    #helper function to convert
    top_genres = models.JSONField(blank = True, default=dict)

    def __str__(self):
        return str(self.id)



    #on hold, currently wraps only have one user
    #def get_users(self):
    #    return list(self.users.all())



