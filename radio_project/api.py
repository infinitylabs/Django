from functools import wraps
from django.http import HttpResponse

class Api(object):
    """Api class that supports multiple output formats, the default is JSONP
    that is included in this file, by default also includes a JSON encoder
    
    You can register new encoders by decorating your encoder function with
    api.register below this class. It requires one required argument, the name
    of the encoder. This name is used to refer to this encoder from then on.
    
    Each encoder should accept three arguments passed to it, which are the
    following. 
    
        Request object from django
    
        The return value of the Decorated function
    
        A dictionary containing extra arguments passed to the API Decorator
        
    How to use the decorator:
    
        You decorate the function that returns a value that can be encoded
        by the various encoders you want it to use. The decorator accepts
        the following arguments.
            
            Parameters:
                - `default`: The default encoder to use if not specified by user.
            
                - `supported`: A list of encoders to allow to be specified by the user.
            
                - Other keyword arguments: These are passed to encoders as the third
                                     argument in their call.
                                     
        Encoders can make use of the extra keyword arguments as they like and
        you should read the documentation on the encoder if you want to know
        what extra keyword arguments they support if any.
        
        Simple example that returns the full User table as a json object:
        
            @api.Api(default='json')
            def userlist(request):
                return User.objects.all()
                
        """
    supported_apis = {}
    def __init__(self, default="jsonp", supported=None, **kwargs):
        super(Api, self).__init__()
        self.default = default.lower()
        self.supported = supported if supported else self.supported_apis
        self.info = kwargs
    def __call__(self, f):
        @wraps(f)
        def api_wrapper(request, *args, **kwargs):
            data = f(request, *args, **kwargs)
            type = request.GET.get("type", self.default)
            if not isinstance(data, HttpResponse):
                encoder = self.supported_apis.get(type, self.default)
                encoder_result = encoder(request, data, self.info)
                if not isinstance(encoder_result, HttpResponse):
                    print "HELLO", type(encoder_result)
                    return HttpResponse(encoder_result) # Wrap it if it didn't return a response
                else:
                    return encoder_result # For when the encoder makes a response
            else:
                return data # For when the original view returns a response
        return api_wrapper
    
def register(name):
    def register_wrap(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            return f(*args, **kwargs)
        Api.supported_apis[name] = wrapped_function
        return wrapped_function
    return register_wrap

import json
from time import mktime
from django.db.models.query import QuerySet
from datetime import datetime
class JSONEncoder(json.JSONEncoder):
    def __init__(self, info, *args, **kwargs):
        super(JSONEncoder, self).__init__(*args, **kwargs)
        if not 'serialize_hint' in info:
            self.hint = {}
        else:
            self.hint = info['serialize_hint']
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
        if hasattr(o, "serialize_hint"):
            rdict = {}
            try:
                for key, value in o.serialize_hint.iteritems():
                    rdict[key] = modelattr(o, value)
                return rdict
            except AttributeError:
                try:
                    return [modelattr(o, value) for value in o.serialize_hint]
                except:
                    return o.serialize_hint
        elif type(o) in self.hint:
            o.serialize_hint = self.hint[type(o)]
            return self.default(o)
        elif isinstance(o, QuerySet):
            return list(o)
        elif isinstance(o, datetime):
            return int(mktime(o.timetuple()))
        else:
            super(JSONEncoder, self).default(o)
            
@register(name="json")
def json_api(request, data, info):
    data = JSONEncoder(info).encode(data)
    return HttpResponse(data, content_type=u"application/json; charset=utf-8")

@register(name="jsonp")
def jsonp_api(request, data, info):
    data = JSONEncoder(info).encode(data) # Encode our data to JSON
    
    resp = HttpResponse(data) # Make response object so we can add headers

    # Wrap into callback, brackets and apply headers
    if 'callback' in request.GET:
        callback= request.GET['callback']
        resp['Content-Type'] = 'text/javascript; charset=utf-8'
        resp.content = "%s(%s)" % (callback, resp.content)
        return resp
    else:
        resp['Content-Type'] = "application/json; charset=utf-8"
        return resp