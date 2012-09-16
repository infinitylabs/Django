import settings
import re
from . import create_index, get_index, WHOOSH_SCHEMA
from .models import Track, CollectionHasTags, TrackHasAlbum, Collection, Songs, Album, Tags
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import QueryParser, WildcardPlugin
from django.db.models import Q

class Writer(object):
    """Simple writer context manager, uses the BufferedWriter for
    better performance"""
    def __init__(self):
        super(Searcher, self).__init__()
        self.ix = get_index()
    def __enter__(self):
        # TODO: Need to check period and limit numbers
        self.writer = BufferedWriter(self.ix, period=120, limit=100)
        return self.writer
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.writer.cancel()
        else:
            self.writer.commit()
            
class mapper(object):
    """Decorator that should be used if you want to register extra
    mapper functions for the Searcher class, see below for examples"""
    def __init__(self, kind):
        self.kind = kind
    def __call__(self, f):
        Searcher.maps[self.kind] = f
        return f

class Searcher(object):
    maps = {} # Where we save our mapping functions
    regex = re.compile(r"([tga]) ([0-9]+)(?: ([0-9]+))?")
    def __init__(self, default="track"):
        super(Searcher, self).__init__()
        self.ix = get_index()
        self.default_kind = default
    def __enter__(self):
        self.searcher = self.ix.searcher()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.searcher.close()
    def search(self, *args, **kwargs):
        """Search method, your entry point to the search engine
        
        Accepts arguments that are passed to the search engine
        search instance, also accepts the following extra arguments:
        
            'kind': The kind of object you want returned, the default is a
                QuerySet that uses Track. supported types are:
                    'track': The default
                    'collection': Uses Collection
                    'songs': Uses Songs*
                    'album': Uses Album*
                    'tag': Uses Tags*
                    
                    *: Can return more or less objects than search results due to
                    linking.
        """
        try:
            kind = kwargs['kind']
            del kwargs['kind']
        except KeyError:
            kind = self.default_kind
        
        result = self.searcher.search(*args, **kwargs)
        return self.map(result, kind)
    def map(self, result, kind):
        """Loops over search results and puts them in usable sequences that
        are passed to individual mappers depending on output format.
        
        There are three sequences passed to the mapper these are:
            track_list: a list of track.id's
            album_list: a list of track.id's
            tag_list: a list of collection.id's
            
            """
        mapper = self.maps.get(kind, self.maps.get("track"))

        track_list, tag_list, album_list = [], [], []
        for link in [item['link'] for item in result]:
            try:
                r = self.regex.match(link).groups()
            except AttributeError:
                # No match? Faulty data report it
                logging.error("Invalid data from search result: %s", link)
                continue
            if r[0] == u't': # Track entry
                track_list.append(r[1])
            elif r[0] == u'g': # Tag entry
                tag_list.append(r[2])
            elif r[0] == u'a': # Album entry
                album_list.append(r[2])
        return mapper(track_list, tag_list, album_list)
    
@mapper(kind="tags")
def map_tags(self, tracks, tags, albums):
    tracks = tracks+albums
    query = Q(collectionhastags__collection__songs__track__in=tracks) | Q(collectionhastags__collection__id__in=tags)
    return Tags.objects.filter(query)

@mapper(kind="album")
def map_album(self, tracks, tags, albums):
    tracks = tracks+albums
    query = Q(trackhasalbum__track__in=tracks) | Q(trackhasalbum__track__songs__collection__id__in=tags)
    return Album.objects.filter(query)

@mapper(kind="songs")
def map_songs(self, tracks, tags, albums):
    tracks = tracks+albums
    query = Q(track__id__in=tracks) | Q(collection__id__in=tags)
    return Songs.objects.filter(query)

@mapper(kind="collection")
def map_collection(self, tracks, tags, albums):
    tracks = tracks+albums
    query = Q(songs__track__in=tracks) | Q(id__in=tags)
    return Collection.objects.filter(query)
    
@mapper(kind="track")
def map_track(tracks, tags, albums):
    """Maps a whoosh result set to Django database models"""
    tracks = tracks+albums
    query = Q(id__in=tracks) | Q(songs__collection__in=tags)
    return Track.objects.filter(query)

class SiteParser(QueryParser):
    """Default whoosh parser for website usage, it disables the WildcardPlugin because
    it can affect performance if used wrongly"""
    def __init__(self, *args, **kwargs):
        super(SiteParser, self).__init__("content", WHOOSH_SCHEMA, *args, **kwargs)
        self.remove_plugin_class(WildcardPlugin)
        
def fill_index():
    """Creates if doesn't exist and fills the whoosh index with the whole
    database"""
    create_index()
    with Writer() as writer:
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
        
def query_parser(f):
    """Simple convenience decorator, it creates a whoosh Query object from
    the first argument of the function decorated"""
    from functools import wraps
    @wraps(f)
    def query_wrapper(query, *args, **kwargs):
        return f(SiteParser().parse(query), *args, **kwargs)
    return query_wrapper

@query_parser
def search(query, *args, **kwargs):
    """Simple search method, should be used for testing only. Use the actual
    Searcher class for searching inside views"""
    with Searcher() as s:
        return s.search(query, *args, **kwargs)