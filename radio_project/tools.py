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

from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
def pagination(obj, page_size=20, page=1):
    """Uses: https://docs.djangoproject.com/en/1.3/topics/pagination/
    
    Paginator for 'obj' returns the items on the page requested where:
        
        obj = Object to paginate
        page_size = Items on a single page
        page = The page to retrieve
        
        Usage:
            >>> pagination([1, 2, 3, 4, 5, 6], page_size=2, page=2)
            [3, 4]
    """
    paginator = Paginator(obj, page_size)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items