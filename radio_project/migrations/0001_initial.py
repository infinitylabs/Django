# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RadioUser'
        db.create_table(u'radio_user', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('google_token', self.gf('django.db.models.fields.TextField')(null=True)),
            ('nickname', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Nicknames'], null=True)),
        ))
        db.send_create_signal('radio_project', ['RadioUser'])

        # Adding model 'Djs'
        db.create_table(u'djs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], db_column=u'user')),
            ('theme', self.gf('django.db.models.fields.CharField')(default=u'default', max_length=60)),
        ))
        db.send_create_signal('radio_project', ['Djs'])

        # Adding model 'News'
        db.create_table(u'news', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('commenting', self.gf('django.db.models.fields.IntegerField')()),
            ('poster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], db_column=u'poster')),
        ))
        db.send_create_signal('radio_project', ['News'])

        # Adding model 'NewsComments'
        db.create_table(u'news_comments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('news', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.News'])),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('mail', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('poster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, db_column=u'poster', blank=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('radio_project', ['NewsComments'])

        # Adding model 'Tracks'
        db.create_table(u'tracks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('radio_project', ['Tracks'])

        # Adding model 'Songs'
        db.create_table(u'songs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=45)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'])),
        ))
        db.send_create_signal('radio_project', ['Songs'])

        # Adding model 'Albums'
        db.create_table(u'albums', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, blank=True)),
        ))
        db.send_create_signal('radio_project', ['Albums'])

        # Adding model 'Collection'
        db.create_table(u'collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'], unique=True)),
            ('usable', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('filename', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('good_upload', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('need_reupload', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('popularity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('decline_reason', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
        ))
        db.send_create_signal('radio_project', ['Collection'])

        # Adding model 'CollectionEditors'
        db.create_table(u'collection_editors', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=45, blank=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Collection'])),
        ))
        db.send_create_signal('radio_project', ['CollectionEditors'])

        # Adding model 'Tags'
        db.create_table(u'tags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, blank=True)),
        ))
        db.send_create_signal('radio_project', ['Tags'])

        # Adding model 'TrackHasTags'
        db.create_table(u'track_has_tags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tags'])),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'])),
        ))
        db.send_create_signal('radio_project', ['TrackHasTags'])

        # Adding unique constraint on 'TrackHasTags', fields ['tag', 'track']
        db.create_unique(u'track_has_tags', ['tag_id', 'track_id'])

        # Adding model 'Hostnames'
        db.create_table(u'hostnames', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('radio_project', ['Hostnames'])

        # Adding model 'Nicknames'
        db.create_table(u'nicknames', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('passcode', self.gf('django.db.models.fields.CharField')(max_length=8, null=True)),
            ('hostname', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Hostnames'])),
        ))
        db.send_create_signal('radio_project', ['Nicknames'])

        # Adding model 'NicknameAlias'
        db.create_table(u'nickname_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('nickname', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'names', to=orm['radio_project.Nicknames'])),
        ))
        db.send_create_signal('radio_project', ['NicknameAlias'])

        # Adding model 'Players'
        db.create_table(u'players', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45, null=True)),
            ('useragent', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, blank=True)),
        ))
        db.send_create_signal('radio_project', ['Players'])

        # Adding model 'Listeners'
        db.create_table(u'listeners', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, blank=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Players'], null=True, blank=True)),
            ('banned', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')()),
            ('nicknames', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Nicknames'], null=True, blank=True)),
        ))
        db.send_create_signal('radio_project', ['Listeners'])

        # Adding model 'CurrentListeners'
        db.create_table(u'current_listeners', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('listeners', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Listeners'])),
        ))
        db.send_create_signal('radio_project', ['CurrentListeners'])

        # Adding model 'Faves'
        db.create_table(u'faves', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Songs'])),
            ('nickname', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Nicknames'])),
        ))
        db.send_create_signal('radio_project', ['Faves'])

        # Adding unique constraint on 'Faves', fields ['nickname', 'song']
        db.create_unique(u'faves', ['nickname_id', 'song_id'])

        # Adding model 'DJFaves'
        db.create_table(u'dj_faves', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('dj', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Djs'])),
            ('nicknames', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Nicknames'])),
        ))
        db.send_create_signal('radio_project', ['DJFaves'])

        # Adding unique constraint on 'DJFaves', fields ['nicknames', 'dj']
        db.create_unique(u'dj_faves', ['nicknames_id', 'dj_id'])

        # Adding model 'Played'
        db.create_table(u'played', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Songs'])),
            ('dj', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Djs'])),
        ))
        db.send_create_signal('radio_project', ['Played'])

        # Adding model 'Queue'
        db.create_table(u'queue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('dj', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Djs'])),
        ))
        db.send_create_signal('radio_project', ['Queue'])

        # Adding model 'Relays'
        db.create_table(u'relays', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('relay_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('relay_owner', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('base_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
            ('mount', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')()),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('listeners', self.gf('django.db.models.fields.IntegerField')()),
            ('listener_limit', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.IntegerField')()),
            ('admin_auth', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('radio_project', ['Relays'])

        # Adding model 'Requests'
        db.create_table(u'requests', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'])),
            ('listeners', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Listeners'])),
            ('hostnames', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Hostnames'])),
        ))
        db.send_create_signal('radio_project', ['Requests'])

        # Adding model 'Streamstatus'
        db.create_table(u'streamstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('listener_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'])),
            ('dj', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Djs'])),
        ))
        db.send_create_signal('radio_project', ['Streamstatus'])

        # Adding model 'TrackHasAlbum'
        db.create_table(u'track_has_album', (
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'], primary_key=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Albums'])),
        ))
        db.send_create_signal('radio_project', ['TrackHasAlbum'])

        # Adding unique constraint on 'TrackHasAlbum', fields ['track', 'album']
        db.create_unique(u'track_has_album', ['track_id', 'album_id'])

        # Adding model 'Artists'
        db.create_table(u'artist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mbid', self.gf('django.db.models.fields.CharField')(max_length=36, null=True, db_index=True)),
        ))
        db.send_create_signal('radio_project', ['Artists'])

        # Adding model 'TrackHasArtist'
        db.create_table(u'track_has_artist', (
            ('track', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Tracks'], primary_key=True)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Artists'])),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('seperator', self.gf('django.db.models.fields.CharField')(default=u'', max_length=20)),
        ))
        db.send_create_signal('radio_project', ['TrackHasArtist'])

        # Adding unique constraint on 'TrackHasArtist', fields ['track', 'artist']
        db.create_unique(u'track_has_artist', ['track_id', 'artist_id'])

        # Adding model 'ArtistHasAlias'
        db.create_table(u'artist_has_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('artist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Artists'])),
            ('alias', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.ArtistAlias'])),
        ))
        db.send_create_signal('radio_project', ['ArtistHasAlias'])

        # Adding unique constraint on 'ArtistHasAlias', fields ['artist', 'alias']
        db.create_unique(u'artist_has_alias', ['artist_id', 'alias_id'])

        # Adding model 'ArtistAlias'
        db.create_table(u'artist_alias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('radio_project', ['ArtistAlias'])

        # Adding model 'Uploads'
        db.create_table(u'uploads', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('listener', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Listeners'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radio_project.Collection'])),
        ))
        db.send_create_signal('radio_project', ['Uploads'])

        # Adding model 'Radvars'
        db.create_table(u'radvars', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('radio_project', ['Radvars'])


    def backwards(self, orm):
        # Removing unique constraint on 'ArtistHasAlias', fields ['artist', 'alias']
        db.delete_unique(u'artist_has_alias', ['artist_id', 'alias_id'])

        # Removing unique constraint on 'TrackHasArtist', fields ['track', 'artist']
        db.delete_unique(u'track_has_artist', ['track_id', 'artist_id'])

        # Removing unique constraint on 'TrackHasAlbum', fields ['track', 'album']
        db.delete_unique(u'track_has_album', ['track_id', 'album_id'])

        # Removing unique constraint on 'DJFaves', fields ['nicknames', 'dj']
        db.delete_unique(u'dj_faves', ['nicknames_id', 'dj_id'])

        # Removing unique constraint on 'Faves', fields ['nickname', 'song']
        db.delete_unique(u'faves', ['nickname_id', 'song_id'])

        # Removing unique constraint on 'TrackHasTags', fields ['tag', 'track']
        db.delete_unique(u'track_has_tags', ['tag_id', 'track_id'])

        # Deleting model 'RadioUser'
        db.delete_table(u'radio_user')

        # Deleting model 'Djs'
        db.delete_table(u'djs')

        # Deleting model 'News'
        db.delete_table(u'news')

        # Deleting model 'NewsComments'
        db.delete_table(u'news_comments')

        # Deleting model 'Tracks'
        db.delete_table(u'tracks')

        # Deleting model 'Songs'
        db.delete_table(u'songs')

        # Deleting model 'Albums'
        db.delete_table(u'albums')

        # Deleting model 'Collection'
        db.delete_table(u'collection')

        # Deleting model 'CollectionEditors'
        db.delete_table(u'collection_editors')

        # Deleting model 'Tags'
        db.delete_table(u'tags')

        # Deleting model 'TrackHasTags'
        db.delete_table(u'track_has_tags')

        # Deleting model 'Hostnames'
        db.delete_table(u'hostnames')

        # Deleting model 'Nicknames'
        db.delete_table(u'nicknames')

        # Deleting model 'NicknameAlias'
        db.delete_table(u'nickname_alias')

        # Deleting model 'Players'
        db.delete_table(u'players')

        # Deleting model 'Listeners'
        db.delete_table(u'listeners')

        # Deleting model 'CurrentListeners'
        db.delete_table(u'current_listeners')

        # Deleting model 'Faves'
        db.delete_table(u'faves')

        # Deleting model 'DJFaves'
        db.delete_table(u'dj_faves')

        # Deleting model 'Played'
        db.delete_table(u'played')

        # Deleting model 'Queue'
        db.delete_table(u'queue')

        # Deleting model 'Relays'
        db.delete_table(u'relays')

        # Deleting model 'Requests'
        db.delete_table(u'requests')

        # Deleting model 'Streamstatus'
        db.delete_table(u'streamstatus')

        # Deleting model 'TrackHasAlbum'
        db.delete_table(u'track_has_album')

        # Deleting model 'Artists'
        db.delete_table(u'artist')

        # Deleting model 'TrackHasArtist'
        db.delete_table(u'track_has_artist')

        # Deleting model 'ArtistHasAlias'
        db.delete_table(u'artist_has_alias')

        # Deleting model 'ArtistAlias'
        db.delete_table(u'artist_alias')

        # Deleting model 'Uploads'
        db.delete_table(u'uploads')

        # Deleting model 'Radvars'
        db.delete_table(u'radvars')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'radio_project.albums': {
            'Meta': {'object_name': 'Albums', 'db_table': "u'albums'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['radio_project.Tracks']", 'through': "orm['radio_project.TrackHasAlbum']", 'symmetrical': 'False'})
        },
        'radio_project.artistalias': {
            'Meta': {'object_name': 'ArtistAlias', 'db_table': "u'artist_alias'"},
            'artist': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'names'", 'symmetrical': 'False', 'through': "orm['radio_project.ArtistHasAlias']", 'to': "orm['radio_project.Artists']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'radio_project.artisthasalias': {
            'Meta': {'unique_together': "((u'artist', u'alias'),)", 'object_name': 'ArtistHasAlias', 'db_table': "u'artist_has_alias'"},
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.ArtistAlias']"}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Artists']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'radio_project.artists': {
            'Meta': {'object_name': 'Artists', 'db_table': "u'artist'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mbid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'db_index': 'True'}),
            'track': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'artist'", 'null': 'True', 'through': "orm['radio_project.TrackHasArtist']", 'to': "orm['radio_project.Tracks']"})
        },
        'radio_project.collection': {
            'Meta': {'object_name': 'Collection', 'db_table': "u'collection'"},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'decline_reason': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'filename': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'good_upload': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need_reupload': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']", 'unique': 'True'}),
            'usable': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'radio_project.collectioneditors': {
            'Meta': {'object_name': 'CollectionEditors', 'db_table': "u'collection_editors'"},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '45', 'blank': 'True'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'radio_project.currentlisteners': {
            'Meta': {'object_name': 'CurrentListeners', 'db_table': "u'current_listeners'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listeners': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Listeners']"})
        },
        'radio_project.djfaves': {
            'Meta': {'unique_together': "((u'nicknames', u'dj'),)", 'object_name': 'DJFaves', 'db_table': "u'dj_faves'"},
            'dj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Djs']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nicknames': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Nicknames']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'radio_project.djs': {
            'Meta': {'object_name': 'Djs', 'db_table': "u'djs'"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "u'default'", 'max_length': '60'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'db_column': "u'user'"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'radio_project.faves': {
            'Meta': {'unique_together': "((u'nickname', u'song'),)", 'object_name': 'Faves', 'db_table': "u'faves'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Nicknames']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Songs']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'radio_project.hostnames': {
            'Meta': {'object_name': 'Hostnames', 'db_table': "u'hostnames'"},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'radio_project.listeners': {
            'Meta': {'object_name': 'Listeners', 'db_table': "u'listeners'"},
            'banned': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'nicknames': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Nicknames']", 'null': 'True', 'blank': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Players']", 'null': 'True', 'blank': 'True'})
        },
        'radio_project.news': {
            'Meta': {'object_name': 'News', 'db_table': "u'news'"},
            'commenting': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'db_column': "u'poster'"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        'radio_project.newscomments': {
            'Meta': {'object_name': 'NewsComments', 'db_table': "u'news_comments'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'news': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.News']"}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'poster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'db_column': "u'poster'", 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'radio_project.nicknamealias': {
            'Meta': {'object_name': 'NicknameAlias', 'db_table': "u'nickname_alias'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'nickname': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'names'", 'to': "orm['radio_project.Nicknames']"})
        },
        'radio_project.nicknames': {
            'Meta': {'object_name': 'Nicknames', 'db_table': "u'nicknames'"},
            'hostname': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Hostnames']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passcode': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True'})
        },
        'radio_project.played': {
            'Meta': {'object_name': 'Played', 'db_table': "u'played'"},
            'dj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Djs']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Songs']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'radio_project.players': {
            'Meta': {'object_name': 'Players', 'db_table': "u'players'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True'}),
            'useragent': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'})
        },
        'radio_project.queue': {
            'Meta': {'object_name': 'Queue', 'db_table': "u'queue'"},
            'dj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Djs']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'radio_project.radiouser': {
            'Meta': {'object_name': 'RadioUser', 'db_table': "u'radio_user'", '_ormbases': ['auth.User']},
            'google_token': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'nickname': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Nicknames']", 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'radio_project.radvars': {
            'Meta': {'object_name': 'Radvars', 'db_table': "u'radvars'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'radio_project.relays': {
            'Meta': {'object_name': 'Relays', 'db_table': "u'relays'"},
            'active': ('django.db.models.fields.IntegerField', [], {}),
            'admin_auth': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'base_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'listeners': ('django.db.models.fields.IntegerField', [], {}),
            'mount': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'relay_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'relay_owner': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'radio_project.requests': {
            'Meta': {'object_name': 'Requests', 'db_table': "u'requests'"},
            'hostnames': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Hostnames']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listeners': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Listeners']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']"})
        },
        'radio_project.songs': {
            'Meta': {'object_name': 'Songs', 'db_table': "u'songs'"},
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']"})
        },
        'radio_project.streamstatus': {
            'Meta': {'object_name': 'Streamstatus', 'db_table': "u'streamstatus'"},
            'dj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Djs']"}),
            'end_time': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']"})
        },
        'radio_project.tags': {
            'Meta': {'object_name': 'Tags', 'db_table': "u'tags'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'tracks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['radio_project.Tracks']", 'through': "orm['radio_project.TrackHasTags']", 'symmetrical': 'False'})
        },
        'radio_project.trackhasalbum': {
            'Meta': {'unique_together': "((u'track', u'album'),)", 'object_name': 'TrackHasAlbum', 'db_table': "u'track_has_album'"},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Albums']"}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']", 'primary_key': 'True'})
        },
        'radio_project.trackhasartist': {
            'Meta': {'unique_together': "((u'track', u'artist'),)", 'object_name': 'TrackHasArtist', 'db_table': "u'track_has_artist'"},
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Artists']"}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'seperator': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '20'}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']", 'primary_key': 'True'})
        },
        'radio_project.trackhastags': {
            'Meta': {'unique_together': "((u'tag', u'track'),)", 'object_name': 'TrackHasTags', 'db_table': "u'track_has_tags'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tags']"}),
            'track': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Tracks']"})
        },
        'radio_project.tracks': {
            'Meta': {'object_name': 'Tracks', 'db_table': "u'tracks'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'radio_project.uploads': {
            'Meta': {'object_name': 'Uploads', 'db_table': "u'uploads'"},
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Collection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radio_project.Listeners']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['radio_project']