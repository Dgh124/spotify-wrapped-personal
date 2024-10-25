import uuid

from django.db import models

class User(models.Model):
    spotify_id = models.CharField(max_length=22, default=0, primary_key=True)
    display_name = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.display_name

class Wrap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.id