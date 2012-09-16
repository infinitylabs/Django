"""Various tool found through our journey!"""
from django.http import HttpResponse
from functools import wraps, update_wrapper
import json
from django.db.models.query import QuerySet
from datetime import datetime
from time import mktime

class JSONEncoder(json.JSONEncoder):
    def __init__(self, hint=None, *args, **kwargs):
        super(JSONEncoder, self).__init__(*args, **kwargs)
        if not hint:
            self.hint = {}
        else:
            self.hint = hint
    @classmethod
    def modelattr(cls, object, attribute):
        """Returns an attribute accepting django notation for multiple depth"""
        for attr in attribute.split("__"):
            if attr.endswith('!'):
                object = getattr(object, attr[:-1])()
            else:
                object = getattr(object, attr)
        return object
    
    def default(self, o):
        modelattr = self.modelattr
        if hasattr(o, "json_hint"):
            rdict = {}
            try:
                for key, value in o.json_hint.iteritems():
                    rdict[key] = modelattr(o, value)
                return rdict
            except AttributeError:
                try:
                    return [modelattr(o, value) for value in o.json_hint]
                except:
                    return o.json_hint
        elif type(o) in self.hint:
            o.json_hint = self.hint[type(o)]
            return self.default(o)
        elif isinstance(o, QuerySet):
            return list(o)
        elif isinstance(o, datetime):
            return mktime(o.timetuple())
        else:
            super(JSONEncoder, self).default(o)
            
class json_wrap(object):
    """"""
    def __init__(self, hint=None):
        self.hint = hint
    def __call__(self, f):
        @wraps(f)
        def json_wrapper(request, *args, **kwargs):
            data = f(request, *args, **kwargs)
            return HttpResponse(JSONEncoder(hint=self.hint).encode(data), content_type="application/json")
        return json_wrapper

def jsonp(f): # https://gist.github.com/871954
    """Wrap a json response in a callback, and set the mimetype (Content-Type) header accordingly
    (will wrap in text/javascript if there is a callback). If the "callback" or "jsonp" paramters
    are provided, will wrap the json output in callback({thejson})
    Usage:
        @jsonp
        def my_json_view(request):
        d = { 'key': 'value' }
        return HTTPResponse(json.dumps(d), content_type='application/json')
    """
    from functools import wraps
    @wraps(f)
    def jsonp_wrapper(request, *args, **kwargs):
        resp = f(request, *args, **kwargs)
        if resp.status_code != 200:
            return resp
        if 'callback' in request.GET:
            callback= request.GET['callback']
            resp['Content-Type']='text/javascript; charset=utf-8'
            resp.content = "%s(%s)" % (callback, resp.content)
            return resp
        elif 'jsonp' in request.GET:
            callback= request.GET['jsonp']
            resp['Content-Type']='text/javascript; charset=utf-8'
            resp.content = "%s(%s)" % (callback, resp.content)
            return resp
        else:
            return resp
                
    return jsonp_wrapper

def lp_time_format(date):
    """Formats a datetime.datetime object into a time for the Last Played page"""
    import datetime
    now = datetime.datetime.now()
    delta = now - date
    if delta.days >= 1:
        return "{days} day{s} ago".format(days=delta.days, s=('' if delta.days == 1 else 's'))
    else:
        return date.strftime('%H:%M:%S')

def queue_time_format(date):
    """Formats a datetime.datetime object into a time for the Queue page"""
    return date.strftime('%H:%M:%S')

def search_time_format(date):
    """Formats a datetime.datetime object into a time for the Search page"""
    return date.strftime('%a %d %b, %H:%M')

from django.core.paginator import InvalidPage, Paginator as _Paginator
class Paginator(_Paginator):
    def get_context(self, page, range_gap=5):
        try:
            page = int(page)
        except (ValueError, TypeError) as err:
            raise InvalidPage, err
        
        paginator = self.page(page)
        
        if page > 5:
            start = page - range_gap
        else:
            start = 1
            
        if page < self.num_pages - range_gap:
            end = page + range_gap + 1
        else:
            end = self.num_pages + 1
            
        context = {
           "page_range": range(start, end),
           "objects": paginator.object_list,
           "num_pages": self.num_pages,
           "page": page,
           "has_pages": self.num_pages > 1,
           "has_previous": paginator.has_previous(),
           "has_next": paginator.has_next(),
           "previous_page": paginator.previous_page_number(),
           "next_page": paginator.next_page_number(),
           "is_first": page == 1,
           "is_last": page == self.num_pages,
           }
        return context
    
class Link(object):
    """Simple class that collects the multiple objects into it
    Does not accept positional arguments
    
    NOTE ABOUT __nonzero__:
        The current one loops over all the items linked, and checks their
        boolean value. If any of them return True the whole Link object will
        be seen as True.
        
    Usage:
        >>> l = Link(magic="World", hello="Hello")
        >>> l.magic
        "World"
        >>> l.hello
        "Hello"
    """
    def __init__(self, **kwargs):
        super(Link, self).__init__()
        self._items = []
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
            self._items.append(value)
    def __nonzero__(self):
        for items in self._items:
            if items:
                return True
        return False
