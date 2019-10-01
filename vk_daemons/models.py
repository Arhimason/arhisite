# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class UserAllInf(models.Model):
    LOG = models.TextField(blank=True)
    id = models.CharField(max_length=20, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    group = models.CharField(max_length=20, default='None')
    status = models.CharField(max_length=150, blank=True)
    status_audio = models.CharField(max_length=100, blank=True)
    deactivated = models.CharField(max_length=10, blank=True)
    bdate = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    home_town = models.CharField(max_length=50, blank=True)
    home_phone = models.CharField(max_length=30, blank=True)
    mobile_phone = models.CharField(max_length=30, blank=True)
    skype = models.CharField(max_length=30, blank=True)
    facebook = models.CharField(max_length=30, blank=True)
    facebook_name = models.CharField(max_length=30, blank=True)
    twitter = models.CharField(max_length=30, blank=True)
    livejournal = models.CharField(max_length=30, blank=True)
    instagram = models.CharField(max_length=30, blank=True)
    site = models.CharField(max_length=200, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    domain = models.CharField(max_length=50, blank=True)
    relatives = models.CharField(max_length=300, blank=True)
    relation = models.CharField(max_length=3, blank=True)
    relation_partner = models.CharField(max_length=100, blank=True)
    connections = models.CharField(max_length=300, blank=True)
    personal = models.CharField(max_length=200, blank=True)
    activities = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    music = models.TextField(blank=True)
    movies = models.TextField(blank=True)
    tv = models.TextField(blank=True)
    books = models.TextField(blank=True)
    games = models.TextField(blank=True)
    about = models.TextField(blank=True)
    quotes = models.TextField(blank=True)
    universities = models.TextField(blank=True)
    schools = models.TextField(blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    LOG_modified_time = models.DateTimeField(null=True)
    # LastCheck_time = models.DateTimeField()
    # Enabled = models.BooleanField()

# Create your models here.
