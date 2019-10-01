from django.db import models


# Create your models here.


class Bot(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    access_token = models.CharField(max_length=100)
    latest_chat = models.IntegerField(default=0)


class Chat(models.Model):
    id_my = models.IntegerField(unique=True, primary_key=True)
    bots_data = models.TextField()
    antikick = models.BooleanField(default=False)
