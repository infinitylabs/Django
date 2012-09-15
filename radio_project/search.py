from . import get_index, create_index, update_index_tag, update_index_track, update_index_album
from whoosh import store, index
import settings
from .models import Track, CollectionHasTags, TrackHasAlbum
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import QueryParser

def fill_index():
    create_index()
    storage = FileStorage(settings.WHOOSH_INDEX)
    ix = storage.open_index(indexname="search")
    with ix.writer() as writer:
        print "Starting track adding"
        for instance in Track.objects.all():
            if Track.objects.filter(songs__collection__isnull=False,
                        id=instance.id):
                kind = u"collection"
            else:
                kind = u"track"
            writer.add_document(kind=kind,
                                content=instance.metadata,
                                link=u"t {:d}".format(instance.id))
        print "Starting Tag adding"
        for instance in CollectionHasTags.objects.all():
            writer.add_document(kind=u"tag",
                                content=instance.tags.name,
                                link=u"g {:d} {:d}".format(instance.tags_id, instance.collection_id))
        print "Starting Album adding"
        for instance in TrackHasAlbum.objects.all():
            writer.add_document(kind=u"album",
                                content=instance.album.name,
                                link=u"a {:d} {:d}".format(instance.album_id, instance.track_id))
        print "Committing"
        
def search(query):
    # simple test search
    ix = get_index()
    with ix.searcher() as searcher:
        return searcher.search(QueryParser("content", ix.schema).parse(query))
    
def query(query):
    ix = get_index()
    return QueryParser("content", ix.schema).parse(query)