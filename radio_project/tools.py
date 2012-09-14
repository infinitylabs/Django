"""Various tool found through our journey!"""

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
    
    Usage:
        >>> l = Link(magic="World", hello="Hello")
        >>> l.magic
        "World"
        >>> l.hello
        "Hello"
    """
    def __init__(self, **kwargs):
        super(Link, self).__init__()
        for key, value in kwargs.iteritems():
            setattr(self, key, value)