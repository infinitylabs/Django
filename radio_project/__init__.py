import os
from django.db.models.signals import post_syncdb, post_save
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from whoosh import store, fields, index
from whoosh.filedb.filestore import FileStorage
from radio_project.models import Track, CollectionHasTags, TrackHasAlbum

"""
    Schema format:
        'kind' is the kind of value can be 'tag', 'album' and 'track'
        
        'content' the actual value we are searching
        
        'link' the required information to get database entries 
        back later these are the following:
            The first part is the kind of value where:
                t = track
                g = tag
                a = album
            The second part is the id that can consist of two
            id's when the 'kind' is 'album' or 'tag' due to
            relationships. Examples:
            
            A track entry
                t 300
                
                Where the id is the track ID
            A tag entry
                g 200 300
                
                Where the first id is the tag ID and 
                the second id is the collection ID
                
            A album entry
                a 100 300
                
                Where the first id is the album ID and
                the second is is the track ID
            
"""
WHOOSH_SCHEMA = fields.Schema(kind=fields.ID,
                              content=fields.TEXT,
                              link=fields.IDLIST(stored=True, unique=True))

@receiver(post_syncdb)
def create_index(sender=None, **kwargs):
    if not os.path.exists(settings.WHOOSH_INDEX):
        os.mkdir(settings.WHOOSH_INDEX)
        storage = FileStorage(settings.WHOOSH_INDEX)
        ix = storage.create_index(schema=WHOOSH_SCHEMA,
                                  indexname="search")

@receiver(post_save, sender=Track)
def update_index_track(sender, instance, created, **kwargs):
    storage = FileStorage(settings.WHOOSH_INDEX)
    ix = storage.open_index(indexname="search")
    writer = ix.writer()
    if created:
        writer.add_document(kind=u"track",
                            content=instance.metadata,
                            link=u"t {:d}".format(instance.id))
        writer.commit()
    else:
        writer.update_document(kind=u"track",
                               content=instance.metadata,
                            link=u"t {:d}".format(instance.id))
        writer.commit()
    
@receiver(post_save, sender=CollectionHasTags)
def update_index_tag(sender, instance, created, **kwargs):
    storage = FileStorage(settings.WHOOSH_INDEX)
    ix = storage.open_index(indexname="search")
    writer = ix.writer()
    if created:
        writer.add_document(kind=u"tag",
                            content=instance.tags.name,
                            link=u"g {:d} {:d}".format(instance.tags_id, instance.collection_id))
        writer.commit()
    else:
        writer.update_document(kind=u"tag",
                            content=instance.tags.name,
                            link="g {:d} {:d}".format(instance.tags_id, instance.collection_id))
        writer.commit()

@receiver(post_save, sender=TrackHasAlbum)
def update_index_album(sender, instance, created, **kwargs):
    storage = FileStorage(settings.WHOOSH_INDEX)
    ix = storage.open_index(indexname="search")
    writer = ix.writer()
    if created:
        writer.add_document(kind=u"album",
                            content=instance.album.name,
                            link=u"a {:d} {:d}".format(instance.album_id, instance.track_id))
        writer.commit()
    else:
        writer.update_document(kind=u"album",
                            content=instance.album.name,
                            link=u"a {:d} {:d}".format(instance.album_id, instance.track_id))
        writer.commit()