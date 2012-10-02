from ..musicbrainzngs import musicbrainz as m
musicb = m
from .. import analyzer
import re
import logging

_log = logging.getLogger("musicbrainz")
_log.setLevel(logging.DEBUG)
_log.addHandler(logging.StreamHandler())

def least_unicode(strings):
    string_tuples = map(lambda s: (len(s) - len(u''.join([x for x in s if ord(x) < 128])), s), strings)
    return sorted(string_tuples, key=lambda s: s[0])[0][1]


artist_split_regexes = []
def add_split(regex, seperator):
    global artist_split_regexes
    regex = re.compile(regex)
    artist_split_regexes.append((regex, seperator))
    
add_split(r'\&', u'&')
add_split(r' and ', u'and')
add_split(r',', u',')
add_split(r' - ', u'-')
add_split(r'f(?:ea)?t(?:\.|(?<=eat)uring)?', u'feat.')
add_split(r'v(?:ersu)?s\.?', u'vs.')
add_split(r'-', u'-')

def splitable(raw_string):
    for regex, sep in artist_split_regexes:
        if regex.search(raw_string):
            return True
    return False
        
def setup():
    m.set_useragent(u"Hanyuu-sama", u"1.2", u"http://r-a-d.io")

def splitregex(string, index=0):
    while index < len(artist_split_regexes):
        regex, sep = artist_split_regexes[index]
        result = regex.split(string, 1)
        if len(result) > 1:
            return (result[0].strip(), result[1].strip(), index, sep)
        else:
            index += 1
    return (string, u'', 0, u'')

class CheckError(Exception):
    pass

class Title(object):
    """Simple object that knows a little about the recording construct"""
    def __init__(self, recording, rating=1.0):
        super(Title, self).__init__()
        self.recording = recording
        if rating < 0.01:
            rating = 0.05
        self.rating = rating
        self.artists = []
        self._cache = []
        
    def __repr__(self):
        return "<Title>"
    
    def __lt__(self, other):
        return self.rating < other.rating
    def __le__(self, other):
        return self.rating <= other.rating
    def __gt__(self, other):
        return self.rating > other.rating
    def __ge__(self, other):
        return self.rating >= other.rating
    
    def __contains__(self, artist):
        # Expects an Artist object on the left
        try:
            mbid = artist.mbid()
        except AttributeError, KeyError:
            return False
        else:
            # Do we have our cache?
            if not self._cache:
                for artist in self.recording['artist-credit']:
                    if isinstance(artist, dict):
                        # At least it's an artist thing
                        try:
                            self._cache.append(artist['artist']['id'])
                        except:
                            # I don't know why this would fail
                            print u"Wrongly doing things:", artist
            return mbid in self._cache
        return False
    
    @classmethod
    def create_from_musicbrainz(cls, match, max=-1):
        """Helper method to create multiple DictWrappers from a match dict"""
        result, length = [], len(match['recording-list'])
        for i, recording in enumerate(match['recording-list']):
            if i == max:
                break
            new = cls(recording, rating=0.5)
            result.append(new)
        return result
    
class Artist(object):
    """Simple object that knows a little about the artist returned dict"""
    def __init__(self, artist, raw_artist, seperator=u''):
        super(Artist, self).__init__()
        self.artist = artist
        self.seperator = seperator
        self.raw_artist = raw_artist
    @property
    def name(self):
        artists = self.artist.get('alias-list', [])
        artists = [self.artist['name']] + artists
        return least_unicode(artists)
    def __getitem__(self, key):
        return self.artist[key]
    def __setitem__(self, key, value):
        self.artist[key] = value
    def __delitem__(self, key):
        del self.artist[key]
    def __repr__(self):
        try:
            return u"<Artist {:s}>".format(self.name if hasattr(self, 'name') else "no artist").encode('utf-8')
        except UnicodeEncodeError:
            return u"<Artist unicode error>"
        
    def mbid(self):
        return self.artist['id']
    
    @classmethod
    def create_from_musicbrainz(cls, match, raw_string=u'', sep=u'', max=-1):
        """Helper method to create multiple DictWrappers from a match dict"""
        result = []
        for i, artist in enumerate(match['artist-list']):
            if i == max:
                break
            new = cls(artist, raw_string, sep)
            result.append(new)
        return result
    
def search_artists(query, para=False, *args, **kwargs):
    """Search for an artist on musicbrainz
    
    optional `para` parameter is a boolean for enclosing the query with quotes
        for exact matching.
    Rest of parameters are equal to musicbrainz.search_artists"""
    if para:
        print u"Strict:", query
        query = '"{:s}"'.format(query)
    else:
        print u"Non-Strict:", query
    return musicb.search_artists(query, *args, **kwargs)

def search_titles(query, para=False, *args, **kwargs):
    """Search for a title on musicbrainz
    
    optional `para` parameter is a boolean for enclosing the query with quotes
        for exact matching.
    Rest of parameters are equal to musicbrainz.search_recordings"""
    if para:
        print u"Strict:", query
        query = '"{:s}"'.format(query)
    else:
        print u"Non-Strict:", query
    return musicb.search_recordings(query, *args, **kwargs)

def check_artist_parts(string, leftover=u'', index=0, sep=u'', artists=None, result=None):
    """string = part to check
    leftover = the other side of the split (do we even need this part?)
    artists = list to append success matches to (yay mutables)
    """
    if artists is None:
        artists = []
    if string == u'':
        return artists
    _log.debug(u"---------------START---------------")
    _log.debug(u"Starting: {:s} <> {:s} <> {:d} <> {:s}".format(string, leftover, index, sep))
    match = search_artists(string, para=True, limit=1)
    if match[u'artist-list']:
        # woo a match
        _log.debug(u"Match for: {:s}".format(string))
        result.rating *= 1.25
        artists.append(Artist.create_from_musicbrainz(match, raw_string=string, sep=sep))
        while True:
            try:
                if leftover: # do we have stuff left to do?
                    _log.debug(u"Leftover: {:s}".format(leftover))
                    check_artist_parts(*splitregex(leftover, index), artists=artists, result=result)
            except CheckError:
                # Backtrack signal increase split index
                _log.debug(u"Backtracking: {:s} <> {:s} <> {:d} <> {:s}".format(string, leftover, index, sep))
                index += 1
            else:
                _log.debug(u"Finished recursion.")
                break
    else:
        # no match...
        # can we split this part? start a new recursion
        if splitable(string):
            _log.debug(u"Restarting recursion.")
            check_artist_parts(*splitregex(string), artists=artists, result=result)
        else:
            # no splitting, do non-strict instead
            _log.debug(u"No splitting.")
            match = search_artists(query=string, para=False, limit=100)
            if match[u'artist-list']:
                artists.append(Artist.create_from_musicbrainz(match, raw_string=string, sep=sep))
                result.rating *= 1.10
            else:
                raise CheckError # no match on this end backtrack if possible
    _log.debug(u"Exiting: {:s} <> {:s} <> {:d} <> {:s}".format(string, leftover, index, sep))
    return artists

def check_title_part(string, titles=None, result=None):
    if titles is None:
        titles = []
    match = search_titles(string, para=True, limit=1)
    if match[u'recording-list']:
        # Woo exact match
        result.rating *= 1.25
        titles.extend(Title.create_from_musicbrainz(match))
    else:
        # no strict match ;_; do non-strict and return
        match = search_titles(string, limit=100)
        if match[u'recording-list']:
            titles.extend(Title.create_from_musicbrainz(match))
            result.rating *= 1.10
        else:
            # eeeeeeeh no matches at all, fuck
            pass # lol do nothing
    return titles

@analyzer.Analyzer(priority=0)
def analyze(result):
    artists = []
    titles = []
    check_artist_parts(result.raw_artist, artists=artists, result=result)
    #check_artist_parts(*splitregex(result.raw_artist), artists=artists, result=result)
    # We have a list of potential artists now
    # If it's a single entry we assume it's correct, else we check against
    # title results.
    flattened = {}
    for artist_list in artists:
        for artist in artist_list:
            flattened[artist['id']] = artist
            
    # get title suggestions
    check_title_part(result.raw_title, titles=titles, result=result)
    for recording in titles:
        for artist in flattened.itervalues():
            if artist in recording: # check if the recording has this artist
                recording.rating *= 1.25 # increase rating
                recording.artists.append(artist)
    titles.sort() # Sort our recordings on rating
    
    titles_length = len(titles)
    final_titles = []
    if titles_length > 0:
        # We had a match at the very least, did any get an artist?
        if titles_length == 1:
            # only one match makes it easy
            result.title = titles[0]
            result.artists = titles[0].artists
            result.rating *= 1.50 # good match here
            return result
        else:
            # bigger list
            # do a recursion check if any had an artist matched
            for title in titles:
                if title.artists:
                    # This one had artist match
                    final_titles.append(title)
                elif title.rating == 0.5:
                    # No matches here we can break here
                    break
    titles = final_titles # set back to titles
    if titles:
        # We actually have a title or two left! pick the top rated one
        result.title = titles[0]
        result.artists = titles[0].artists
        result.rating *= 1.20 # Not as good as above
        print result.artists
    else:
        # no matches at all on title, return any artists we found
        # with the original title
        result.title = result.raw_title
        # Append any artists we found strict, discard others
        for artist_list in artists:
            if len(artist_list) == 1:
                result.artists.append(artist_list[0]) # Strict artist, include it
            else:
                result.artists.append(artist_list[0].raw_artist) # Raw artist
    return result

setup()