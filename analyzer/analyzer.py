def test(metadata):
    from plugins import musicbrainz
    parser = Parser(metadata)
    return parser

class Result(object):
    """A simple Result object for passing around the various functions

        The rating is a float between 0.0 and 1.0 where higher is better.
        The highest rating should be the Result most likely to be correct"""
    def __init__(self, rating, artist, title):
        super(Result, self).__init__()
        self.rating = rating
        self.raw_artist = artist
        self.raw_title = title
        self.artists = []
        self.titles = []
        
    def __eq__(self, other):
        return ((self.rating, self.artist.lower(), self.title.lower()) ==
                 (other.rating, other.artist.lower(), other.title.lower()))
    def __lt__(self, other):
        return self.rating < other.rating
    def __le__(self, other):
        return self.rating <= other.rating
    def __gt__(self, other):
        return self.rating > other.rating
    def __ge__(self, other):
        return self.rating >= other.rating
    
    def __repr__(self):
        return u"<Result {:f}: {:s} - {:s}>".format(self.rating,
                                             ", ".join([a.name for a in self.artists]),
                                             self.title).encode('utf-8')
class Parser(object):
    """Parser class, first calls each registered `Splitter` function collecting
    all results they spit out and then feeding them all into the `Analyzer`
    functions for rating changes"""
    analyzers = []
    splitters = []
    def __init__(self, metadata):
        super(Parser, self).__init__()
        self.metadata = metadata
        self.results = []
        
    def parse(self):
        for splitter in self.splitters:
            for result in splitter(self.metadata):
                self.results.append(Result(*result))

        for analyzer in self.analyzers:
            for result in self.results:
                analyzer(result)
        self.results.sort(reverse=True)
        return self.results

    
class Analyzer(object):
    """Decorator for an Analyzer"""
    def __init__(self, priority=0):
        super(Analyzer, self).__init__()

    def __call__(self, f):
        Parser.analyzers.append(f)
        return f

class Splitter(object):
    """Decorator for a Splitter"""
    def __init__(self):
        super(Splitter, self).__init__()

    def __call__(self, f):
        Parser.splitters.append(f)
        return f
    
@Splitter()
def simple_splitter(metadata, sep=' - '):
    """A simple splitter that splits on `sep` and returns an iterator
    of tuples that are of the format (rating, artist, title)"""
    seplength = len(sep)
    sepcount = metadata.count(sep)
    if sepcount == 0:
        yield (1.0, u'', metadata)
    elif sepcount == 1:
        result = metadata.split(sep)
        yield (1.0, result[0], result[1])
    else:
        lastposition = 0
        for i in xrange(sepcount):
            position = metadata.find(sep, lastposition)
            artist = metadata[:position]
            title = metadata[position+seplength:]
            yield (1.0/sepcount, artist, title)
            lastposition = position + seplength
