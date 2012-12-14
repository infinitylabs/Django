# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from __future__ import unicode_literals
from django.db import models, transaction
from django.contrib.auth.models import User, UserManager
from analyzer import analyzer

class BaseManager(models.Manager):
    def from_list(self, entry_list):
        """Creates multiple objects with the entry_list. 
        
        If the entry_list contains tuples they will be used as positional arguments.
        
        If the entry_list contains dictionaries they will be used as keyword arguments.
        
        Only one of the two is supported, you can't mix the two.
        """
        entries = []
        for entry in entry_list:
            if isinstance(entry, dict):
                entries.append(self.model(**entry))
            elif isinstance(entry, tuple):
                entries.append(self.model(*entry))
            elif isinstance(entry, basestring):
                entries.append(self.model(entry))
            else:
                raise TypeError("Entry of type '{:s}' is not supported.".format(repr(type(entry))))
        return entries
    
class TrackManager(BaseManager):
    @transaction.commit_on_success
    def create_from_string(self, string, length=0):
        """Creates a Track entry from a single string in the format
        'artist - title'. Will use an advanced splitter at a later point.
        (haha good checkpoint for doc editing here)"""
        # TODO: Update to advanced analyzer
        parser = analyzer.Parser(string)
        parser.analyzers = []
        result = parser.parse()[0]
        
        artists = Artist.factory.from_list([{'names': [result.raw_artist]}])
        track = self.create(title=result.raw_title, length=0)
        for index, artist in enumerate(artists):
            TrackHasArtist.objects.create(track=track, artist=artist,
                                          index=index, seperator=u'')
        return track
        
class SongManager(BaseManager):
    @transaction.commit_on_success
    def create_from_string(self, string, track):
        import hashlib
        hash = hashlib.sha1(string.encode('utf-8')).hexdigest()
        
        song, created = self.get_or_create(hash=hash,
                                           defaults={'track': track})
        return song
    
class ArtistManager(BaseManager):
    @transaction.commit_on_success
    def from_list(self, entry_list):
        """Creates multiple objects with the entry_list. 
        
        This version expects a list of dicts with the following keys:
        
            Required:
                `names`: A list of names, the first name should be the primary
                         name for this Artist.
                         
            Optional:
                `mbid`: A MusicBrainz Identifier.
        """
        entries = []
        for entry in entry_list:
            artist_entry = self.create(mbid=entry.get('mbid', None))
            aliases, primary = [], True
            for name in entry.get('names', []):
                alias = ArtistAlias.objects.create(name=name)
                ArtistHasAlias.objects.create(alias=alias,
                                              artist=artist_entry,
                                              primary=primary)
                primary = False
            entries.append(artist_entry)
        return entries
    
class RadioUser(User):
    """
    A specialized User model for google OAuth support
    
    Might not be permanent if good alternative is found.
    """
    google_token = models.TextField(null=True)
    nickname = models.ForeignKey('Nickname',
                                 help_text="Nickname used for favorite saving.",
                                 null=True)
    
    objects = UserManager()
    class Meta:
        db_table = 'radio_user'
        
class Dj(models.Model):
    """
    This table is used to save DJ specific information about an user.
    
    See the attribute help for more information.
    """
    serialize_hint = ['name', 'description']
    
    name = models.CharField(max_length=45, help_text="Public name to be shown.")
    description = models.TextField(blank=True,
                                   help_text="Description to be shown on staff page.")
    visible = models.BooleanField(default=False,
                                  help_text="Is this DJ visible on the staff page.")
    priority = models.IntegerField(help_text="List priority, higher number is earlier in the list.")
    user = models.ForeignKey(User, db_column='user')
    theme = models.CharField(max_length=60, default='default',
                             help_text="Theme to be used when DJ is on.")
    @property
    def image(self):
        pass
    class Meta:
        db_table = u'dj'
    def __unicode__(self):
        return self.name
        
class News(models.Model):
    """
    This table is used for news posts. It has no gotchas to worry about.
    
    See the attribute help for more information.
    """
    serialize_hint = ['id', 'time', 'title', 'text']
    
    title = models.CharField(max_length=45, help_text="Public title of this news post.")
    time = models.DateTimeField(help_text="The time this news post was created.")
    text = models.TextField(help_text="The content of the news post, may contain HTML.")
    commenting = models.IntegerField(help_text="Indicates if posting comments is allowed on this news post.")
    poster = models.ForeignKey(User, db_column='poster', help_text="The user that created this news post.")
    class Meta:
        db_table = u'news'
    def __unicode__(self):
        return self.title
        
class NewsComment(models.Model):
    """
    This table is used for comments on news posts. No special gotchas
    
    See the attribute help for more information.
    """
    news = models.ForeignKey(News, help_text="The news post this comment is posted on.")
    nickname = models.CharField(max_length=100, blank=True, help_text="The nickname used by the comment author.")
    text = models.TextField(help_text="The content of the comment, may NOT contain HTML.")
    mail = models.CharField(max_length=200, blank=True, help_text="Email address submitted by the author.")
    poster = models.ForeignKey(User, null=True, db_column='poster', blank=True,
                               help_text="The user account of the author. Can be NULL.")
    time = models.DateTimeField(help_text="The time this comment was posted.")
    class Meta:
        db_table = u'news_comment'
    def __unicode__(self):
        return self.poster
        
class Track(models.Model):
    """Center of the database. Needs more documentation."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, help_text="Title of the track.")
    length = models.IntegerField(null=True, blank=True, help_text="Length of the track.")
    
    objects = models.Manager()
    factory = TrackManager()
    @property
    def metadata(self):
        return u"{:s} - {:s}".format(self._join_artists(), self.title)
    def _join_artists(self):
        """Internal method to join artists linked to this with their seperator"""
        result = []
        for artist in self.get_artists():
            if artist.seperator:
                result.append(artist.seperator)
            result.append(artist.name)
        return " ".join(result)
    
    def get_artists(self):
        """Returns the artists of this track with the 'through' Model attributes
        annotated to it. Thus returning `Artist` objects with `index` and 
        `seperator` attributes."""
        artists = []
        for obj in self.trackhasartist_set.all().order_by('index').select_related('artist'):
            artist = obj.artist
            artist.seperator = obj.seperator
            artist.index = obj.index
            artists.append(artist)
        return artists
    
    def get_albums(self):
        """Does same as `get_artists` except does it for `Album`"""
        albums = []
        for obj in self.trackhasalbum_set.all().select_related('album'):
            album = obj.album
            albums.append(album)
        return albums
    
    def get_tags(self):
        """Does same as `get_artists` except does it for `Tag`"""
        tags = []
        for obj in self.trackhastags_set.all().select_related('tags'):
            tag = obj.tags
            tags.append(tag)
        return tags
    
    def get_faves(self):
        return Fave.objects.filter(song__track=self)
    
    class Meta:
        db_table = u'track'
    def __unicode__(self):
        return self.metadata

class Song(models.Model):
    """
    A `Song` entry is the identifier for a track. An explanation.
    
    When a track is played, we receive the metadata from icecast as a single
    string. This string is processed and turned into a `Track` entry later on.
    
    The string mentioned is not saved at all in this table. But instead is
    transformed with the SHA1 hash algorithm and saved.
    
    A `Song` entry defines the string before it is turned into a `Track`
    entry. This process is used because we need a way to identify this same
    metadata string if it is used at a later time.
    
    As a rule of thumb you should think of the `Song` entry as the identifier
    and the `Track` entry as metadata or information about said identifier.
    """
    hash = models.CharField(unique=True, max_length=45, help_text="SHA1 hash of the metadata string identifier.")
    repair_priority = models.IntegerField(default=1, help_text="The priority for tag repair; 0 means no repair at all.")
    track = models.ForeignKey(Track, help_text="Information entry about this identifier.")
    
    objects = models.Manager()
    factory = SongManager()
    
    class Meta:
        db_table = u'song'
    def __unicode__(self):
        return self.hash
        
class Album(models.Model):
    name = models.CharField(unique=True, max_length=200, blank=True, help_text="Album name")
    tracks = models.ManyToManyField(Track, through="TrackHasAlbum")
    class Meta:
        db_table = u'album'
    def __unicode__(self):
        return self.name
        
class Collection(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    REPLACEMENT = 3

    track = models.ForeignKey(Track, unique=True)
    usable = models.IntegerField(default=0, help_text="Can we use this entry in the AFK Streamer?")
    filename = models.TextField(blank=True, help_text="The filename of the track.")
    good_upload = models.BooleanField(default=False, 
                                      help_text="Was this a good upload or not.")
    need_reupload = models.BooleanField(default=False,
                                        help_text="Does this entry require a replacement due to quality or other circumstances.")
    popularity = models.IntegerField(default=0, 
                                     help_text="Popularity of this track. Used by the AFK request system.")
    status = models.IntegerField(default=0,
                                 help_text="In what state is this entry.")
    decline_reason = models.CharField(null=True,
                                      max_length=120,
                                      help_text="Why did this submission get declined.")
    original_filename = models.CharField(null=True,
                                         max_length=200, help_text="The original filename when this entry got uploaded by the user.")
    comment = models.CharField(null=True,
                               max_length=120,
                               help_text="Comment of the uploader")
    class Meta:
        db_table = u'collection'

class CollectionEditor(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=45, blank=True)
    time = models.DateTimeField(null=True, blank=True, db_index=True)
    collection = models.ForeignKey(Collection)
    class Meta:
        db_table = u'collection_editor'
        
class Tag(models.Model):
    name = models.CharField(unique=True, max_length=100, blank=True)
    tracks = models.ManyToManyField(Track, through='TrackHasTag')
    class Meta:
        db_table = u'tag'
    def __unicode__(self):
        return self.name
        
class TrackHasTag(models.Model):
    tag = models.ForeignKey(Tag)
    track = models.ForeignKey(Track)
    class Meta:
        db_table = u'track_has_tag'
        unique_together = ('tag', 'track')
        
class Hostname(models.Model):
    hostname = models.CharField(max_length=150, help_text="IRC Hostname.")
    class Meta:
        db_table = u'hostname'
    def __unicode__(self):
        return self.hostname
        
class Nickname(models.Model):
    passcode = models.CharField(max_length=8, null=True, help_text="A small passcode used for website/nickname linking.")
    hostname = models.ForeignKey(Hostname, help_text="Pointer to hostname entry")
    class Meta:
        db_table = u'nickname'
    def __unicode__(self):
        return "nickname"
        
class NicknameAlias(models.Model):
    name = models.CharField(unique=True, max_length=30, help_text="Nickname on IRC.")
    nickname = models.ForeignKey(Nickname, related_name="names")
    class Meta:
        db_table = u'nickname_alias'
        
class Player(models.Model):
    name = models.CharField(max_length=45, null=True, help_text="Name of this audio player.")
    useragent = models.CharField(unique=True, max_length=200, blank=True, help_text="User agent of this audio player.")
    class Meta:
        db_table = u'player'
    def __unicode__(self):
        return self.name
        
class Listener(models.Model):
    ip = models.CharField(unique=True, max_length=50, blank=True, help_text="IP Address of this listener.")
    player = models.ForeignKey(Player, null=True, blank=True, help_text="What audio player did this listener last use.")
    banned = models.IntegerField(default=0, help_text="Is this listener banned from our service?")
    last_seen = models.DateTimeField(help_text="Time we last saw this listener.")
    nicknames = models.ForeignKey(Nickname, null=True, blank=True, help_text="The IRC nickname of this user. Can be NULL.")
    class Meta:
        db_table = u'listener'
    def __unicode__(self):
        return self.ip
        
class CurrentListener(models.Model):
    listeners = models.ForeignKey(Listener)
    class Meta:
        db_table = u'current_listener'

class Fave(models.Model):
    time = models.DateTimeField(null=True, blank=True, db_index=True,
                                help_text="When was this favorite entry created.")
    song = models.ForeignKey(Song, help_text="Pointer to the track identifier.")
    nickname = models.ForeignKey(Nickname, help_text="What nickname is this favorite owned by.")
    class Meta:
        db_table = u'fave'
        unique_together = ('nickname', 'song')
    def __unicode__(self):
        return str(self.id)
        
class DJFave(models.Model):
    time = models.DateTimeField(null=True, blank=True, db_index=True,
                                help_text="When was this favorite entry created.")
    dj = models.ForeignKey(Dj, help_text="Pointer to the DJ entry.")
    nicknames = models.ForeignKey(Nickname, help_text="What nickname is this favorite owned by.")
    class Meta:
        db_table = u'dj_fave'
        unique_together = ('nicknames', 'dj')
    def __unicode__(self):
        return "DJ faves"
    
class Played(models.Model):
    serialize_hint = {"time": "time",
                 "track": "song__track__metadata",
                 "playcount": "song__played_set__count!",
                 "favecount": "song__faves_set__count!"}
    
    time = models.DateTimeField(null=True, blank=True, db_index=True,
                                help_text="Time this track played.")
    song = models.ForeignKey(Song, help_text="Song identifier.")
    dj = models.ForeignKey(Dj, help_text="Which DJ streamed played this.")
    class Meta:
        db_table = u'played'
    def __unicode__(self):
        return str(self.id)
        
class Queue(models.Model):
    serialize_hint = {"time": "time",
                 "track": "track__metadata"}
    
    type = models.IntegerField(null=True, blank=True, help_text="Is this a request or a normal entry.")
    track = models.ForeignKey(Track, help_text="Track identifier.")
    time = models.DateTimeField(db_index=True, help_text="The estimated time this queue entry should be played.")
    dj = models.ForeignKey(Dj, help_text="Which DJ does this queue belong to.")
    class Meta:
        db_table = u'queue'
    def __unicode__(self):
        return str(self.id)
        
class Relay(models.Model):
    relay_name = models.CharField(max_length=200,
                                  help_text="Public name we use for this relay.")
    relay_owner = models.CharField(max_length=200,
                                   help_text="Owner of this relay.")
    base_name = models.CharField(max_length=200)
    port = models.IntegerField(help_text="The port this relay is run on.")
    mount = models.CharField(max_length=200,
                             help_text="The mountpoint used for the relay.")
    bitrate = models.IntegerField(help_text="The bitrate this mountpoint sends out.")
    format = models.CharField(max_length=15,
                              help_text="The format this mountpoint sends out.")
    priority = models.IntegerField(help_text="The priority of the relay; between 1 and 1000.")
    listeners = models.IntegerField(help_text="The amount of listeners on this relay.")
    listener_limit = models.IntegerField(null=True, blank=True,
                        help_text="The maximum amount of listeners on this relay.")
    active = models.IntegerField(help_text="Is this relay active?")
    admin_auth = models.CharField(max_length=200,
                        help_text="The admin panel password for this relay.")
    class Meta:
        db_table = u'relay'
    def __unicode__(self):
        return self.relay_name
        
class Request(models.Model):
    time = models.DateTimeField(db_index=True, null=True, blank=True,
                                help_text="The time this got requested.")
    track = models.ForeignKey(Track, help_text="The track that got requested.")
    listeners = models.ForeignKey(Listener, help_text="The requesters IP. Filled when website request.")
    hostnames = models.ForeignKey(Hostname, help_text="The requesters hostname. Filled when IRC request.")
    class Meta:
        db_table = u'requests'
    def __unicode__(self):
        return str(self.id)
        
class Streamstatus(models.Model):
    id = models.AutoField(primary_key=True)
    listener_count = models.IntegerField(null=True, blank=True)
    start_time = models.BigIntegerField(null=True, blank=True)
    end_time = models.BigIntegerField(null=True, blank=True)
    track = models.ForeignKey(Track)
    dj = models.ForeignKey(Dj)
    class Meta:
        db_table = u'streamstatus'
    def __unicode__(self):
        return str(self.id)
        
class TrackHasAlbum(models.Model):
    track = models.ForeignKey(Track, primary_key=True)
    album = models.ForeignKey(Album)
    class Meta:
        db_table = u'track_has_album'
        unique_together = ('track', 'album')
        
class Artist(models.Model):
    track = models.ManyToManyField(Track, through='TrackHasArtist', null=True,
                                   related_name='artist')
    mbid = models.CharField(db_index=True, max_length=36, null=True,
                            help_text="The MusicBrainz identifier of this artist.")
    
    objects = models.Manager()
    factory = ArtistManager()
    class Meta:
        db_table = u'artist'
    def get_aliases(self):
        return ", ".join([alias.name for alias in self.names.all()]) or "No Name"
    @property
    def name(self):
        """Returns the primary name of this artist."""
        try:
            return self.names.filter(artisthasalias__primary=True)[0].name
        except IndexError:
            return self.names.all()[0].name
    def __unicode__(self):
        return self.get_aliases()
    
class TrackHasArtist(models.Model):
    track = models.ForeignKey(Track, primary_key=True)
    artist = models.ForeignKey(Artist)
    index = models.IntegerField(help_text="Index in the artist string. Lower is further to the front.")
    seperator = models.CharField(max_length=20, default='', help_text="The seperator used when multiple artist are present. Defaults to empty string.")
    class Meta:
        unique_together = ('track', 'artist')
        db_table = 'track_has_artist'
        
class ArtistHasAlias(models.Model):
    primary = models.BooleanField(help_text="Is this the primary name of this artist?")
    artist = models.ForeignKey('Artist')
    alias = models.ForeignKey('ArtistAlias')
    class Meta:
        unique_together = ("artist", "alias")
        db_table = 'artist_has_alias'
        
class ArtistAlias(models.Model):
    artist = models.ManyToManyField('Artist', through='ArtistHasAlias', related_name='names')
    name = models.CharField(max_length=200, null=False, help_text="Name of the artist.")
    class Meta:
        db_table = u'artist_alias'
    def __unicode__(self):
        return self.name
    
class Upload(models.Model):
    listener = models.ForeignKey(Listener, help_text="The IP of the uploader.")
    time = models.DateTimeField(db_index=True, null=True, blank=True,
                                help_text="The time of upload.")
    collection = models.ForeignKey(Collection, help_text="Collection pointer.")
    class Meta:
        db_table = u'upload'
    def __unicode__(self):
        return str(self.id)

class Radvar(models.Model):
    """A table used for database based variables. Should be used for variables
    that should be shared across multiple applications but don't warrant their
    own table in the database."""
    name = models.CharField(max_length=100, unique=True, help_text="Name of the variable.")
    value = models.CharField(max_length=200, help_text="Value of the variable.")
    class Meta:
        db_table = u'radvar'
    def __unicode__(self):
        return "{:s}:{:s}".format(self.name, self.value)
