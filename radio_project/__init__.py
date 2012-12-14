import os
from django.db.models.signals import post_syncdb, post_save, pre_delete
from django.db.models import signals
from django.dispatch import receiver
from django.conf import settings
from whoosh import store, fields, index
from whoosh.filedb.filestore import FileStorage
from whoosh.writing import BufferedWriter
from radio_project.models import Track, TrackHasTag, TrackHasAlbum

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

def get_index():
    try:
        storage = FileStorage(settings.WHOOSH_INDEX)
        return storage.open_index(indexname="search")
    except IOError:
        # No index? other error?
        create_index()
        storage = FileStorage(settings.WHOOSH_INDEX)
        return storage.open_index(indexname="search")
    
#@receiver(post_syncdb)
def create_index(sender=None, **kwargs):
    """Creates a File based whoosh index, location used is
    settings.WHOOSH_INDEX so make sure that is set"""
    if not os.path.exists(settings.WHOOSH_INDEX):
        os.mkdir(settings.WHOOSH_INDEX)
        storage = FileStorage(settings.WHOOSH_INDEX)
        ix = storage.create_index(schema=WHOOSH_SCHEMA,
                                  indexname="search")

#@receiver(post_save, sender=Track)
def update_index_track(sender, instance, created, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        if Track.objects.filter(song__collection__isnull=False,
                                id=instance.id):
            kind = u"collection"
        else:
            kind = u"track"
        if created:
            writer.add_document(kind=kind,
                                content=instance.metadata,
                                link=u"t {:d}".format(instance.id))
        elif instance.id is not None:
            writer.update_document(kind=kind,
                                   content=instance.metadata,
                                link=u"t {:d}".format(instance.id))
    
#@receiver(post_save, sender=TrackHasTag)
def update_index_tag(sender, instance, created, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        if created:
            writer.add_document(kind=u"tag",
                                content=instance.tags.name,
                                link=u"g {:d} {:d}".format(instance.tags_id, instance.collection_id))
        elif instance.tags_id is not None and instance.collection_id is not None:
            writer.update_document(kind=u"tag",
                                content=instance.tags.name,
                                link=u"g {:d} {:d}".format(instance.tags_id, instance.collection_id))

#@receiver(post_save, sender=TrackHasAlbum)
def update_index_album(sender, instance, created, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        if created:
            writer.add_document(kind=u"album",
                                content=instance.album.name,
                                link=u"a {:d} {:d}".format(instance.album_id, instance.track_id))
        elif instance.album_id is not None and instance.track_id is not None:
            writer.update_document(kind=u"album",
                                content=instance.album.name,
                                link=u"a {:d} {:d}".format(instance.album_id, instance.track_id))
            
#@receiver(pre_delete, sender=Track)
def delete_index_track(sender, instance, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        writer.delete_by_term("link", u"t {:d}".format(instance.id))
        
#@receiver(pre_delete, sender=TrackHasTag)
def delete_index_tag(sender, instance, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        writer.delete_by_term("link", u"g {:d} {:d}".format(instance.tags_id, instance.collection_id))
        
#@receiver(pre_delete, sender=TrackHasAlbum)
def delete_index_album(sender, instance, **kwargs):
    ix = get_index()
    with ix.writer() as writer:
        writer.delete_by_term("link", u"a {:d} {:d}".format(instance.album_id, instance.track_id))