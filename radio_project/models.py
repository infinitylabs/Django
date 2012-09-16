# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Djs(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    description = models.TextField(blank=True)
    image = models.TextField(blank=True)
    visible = models.IntegerField()
    priority = models.IntegerField()
    user = models.ForeignKey(User, db_column='user')
    theme = models.CharField(max_length=60)
    class Meta:
        db_table = u'djs'
    def __unicode__(self):
        return self.name
        
class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45)
    time = models.DateTimeField()
    text = models.TextField()
    commenting = models.IntegerField()
    poster = models.ForeignKey(User, db_column='poster')
    class Meta:
        db_table = u'news'
    def __unicode__(self):
        return self.title
        
class NewsComments(models.Model):
    id = models.AutoField(primary_key=True)
    news = models.ForeignKey(News)
    nickname = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    mail = models.CharField(max_length=200, blank=True)
    poster = models.ForeignKey(User, null=True, db_column='poster', blank=True)
    time = models.DateTimeField()
    class Meta:
        db_table = u'news_comments'
    def __unicode__(self):
        return self.poster
        
class Track(models.Model):
    id = models.AutoField(primary_key=True)
    metadata = models.CharField(max_length=400)
    length = models.IntegerField(null=True, blank=True)
    hash = models.CharField(unique=True, max_length=45)
    class Meta:
        db_table = u'track'
    def __unicode__(self):
        return self.metadata
        
class Songs(models.Model):
    id = models.AutoField(primary_key=True)
    hash = models.CharField(unique=True, max_length=45)
    track = models.ForeignKey(Track)
    class Meta:
        db_table = u'songs'
    def __unicode__(self):
        return self.hash
        
class Album(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=200, blank=True)
    track = models.ManyToManyField(Track, through="TrackHasAlbum")
    class Meta:
        db_table = u'album'
    def __unicode__(self):
        return self.name
        
class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    songs = models.ForeignKey(Songs)
    usable = models.IntegerField()
    filename = models.TextField(blank=True)
    good_upload = models.IntegerField()
    need_reupload = models.IntegerField()
    popularity = models.IntegerField()
    status = models.IntegerField()
    decline_reason = models.CharField(max_length=120)
    comment = models.CharField(max_length=120)
    original_filename = models.CharField(max_length=200)
    class Meta:
        db_table = u'collection'

class CollectionEditors(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(User)
    action = models.CharField(max_length=45, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    collection = models.ForeignKey(Collection)
    class Meta:
        db_table = u'collection_editors'
        
class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100, blank=True)
    class Meta:
        db_table = u'tags'
    def __unicode__(self):
        return self.name
        
class CollectionHasTags(models.Model):
    tags = models.ForeignKey(Tags, primary_key=True)
    collection = models.ForeignKey(Collection)
    class Meta:
        db_table = u'collection_has_tags'

class Hostnames(models.Model):
    id = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=150)
    class Meta:
        db_table = u'hostnames'
    def __unicode__(self):
        return self.hostname
        
class Nicknames(models.Model):
    id = models.AutoField(primary_key=True)
    nick = models.CharField(unique=True, max_length=30, blank=True)
    passcode = models.CharField(max_length=8, blank=True)
    hostnames = models.ForeignKey(Hostnames)
    class Meta:
        db_table = u'nicknames'
    def __unicode__(self):
        return self.nick
        
class Players(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True)
    useragent = models.CharField(unique=True, max_length=200, blank=True)
    class Meta:
        db_table = u'players'
    def __unicode__(self):
        return self.name
        
class Listeners(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(unique=True, max_length=50, blank=True)
    players = models.ForeignKey(Players, null=True, blank=True)
    banned = models.IntegerField()
    last_seen = models.DateTimeField()
    nicknames = models.ForeignKey(Nicknames, null=True, blank=True)
    class Meta:
        db_table = u'listeners'
    def __unicode__(self):
        return self.ip
        
class CurrentListeners(models.Model):
    id = models.AutoField(primary_key=True)
    listeners = models.ForeignKey(Listeners)
    class Meta:
        db_table = u'current_listeners'

class Faves(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True, blank=True)
    songs = models.ForeignKey(Songs)
    nicknames = models.ForeignKey(Nicknames)
    class Meta:
        db_table = u'faves'
    def __unicode__(self):
        return str(self.id)
        
class Played(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True, blank=True)
    songs = models.ForeignKey(Songs)
    djs = models.ForeignKey(Djs)
    class Meta:
        db_table = u'played'
    def __unicode__(self):
        return str(self.id)
        
class Queue(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.IntegerField(null=True, blank=True)
    songs = models.ForeignKey(Songs)
    time = models.DateTimeField()
    class Meta:
        db_table = u'queue'
    def __unicode__(self):
        return str(self.id)
        
class Relays(models.Model):
    id = models.AutoField(primary_key=True)
    relay_name = models.CharField(max_length=200)
    relay_owner = models.CharField(max_length=200)
    base_name = models.CharField(max_length=200)
    port = models.IntegerField()
    mount = models.CharField(max_length=200)
    bitrate = models.IntegerField()
    format = models.CharField(max_length=15)
    listeners = models.IntegerField()
    listener_limit = models.IntegerField(null=True, blank=True)
    active = models.IntegerField()
    admin_auth = models.CharField(max_length=200)
    class Meta:
        db_table = u'relays'
    def __unicode__(self):
        return self.relay_name
        
class Requests(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(null=True, blank=True)
    songs = models.ForeignKey(Songs)
    listeners = models.ForeignKey(Listeners)
    hostnames = models.ForeignKey(Hostnames)
    class Meta:
        db_table = u'requests'
    def __unicode__(self):
        return str(self.id)
        
class Streamstatus(models.Model):
    id = models.AutoField(primary_key=True)
    listener_count = models.IntegerField(null=True, blank=True)
    start_time = models.BigIntegerField(null=True, blank=True)
    end_time = models.BigIntegerField(null=True, blank=True)
    songs = models.ForeignKey(Songs)
    djs = models.ForeignKey(Djs)
    class Meta:
        db_table = u'streamstatus'
    def __unicode__(self):
        return str(self.id)
        
class TrackHasAlbum(models.Model):
    track = models.ForeignKey(Track, primary_key=True)
    album = models.ForeignKey(Album)
    class Meta:
        db_table = u'track_has_album'

class TrackHasTags(models.Model):
    tags = models.ForeignKey(Tags)
    collection = models.ForeignKey(Collection)
    class Meta:
        db_table = u'track_has_tags'

class Uploads(models.Model):
    id = models.AutoField(primary_key=True)
    listeners = models.ForeignKey(Listeners)
    time = models.DateTimeField(null=True, blank=True)
    collection = models.ForeignKey(Collection)
    class Meta:
        db_table = u'uploads'
    def __unicode__(self):
        return str(self.id)

class Radvars(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    class Meta:
        db_table = u'radvars'
    def __unicode__(self):
        return str(self.name) + ":" + str(self.value)
