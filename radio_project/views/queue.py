from django.shortcuts import render_to_response
from ..models import Queue
from django.template.context import RequestContext
from django.http import HttpResponse
import json
from ..tools import jsonp, json_wrap

def get_content(request):
    return Queue.objects.only("songs__track__metadata", "time")

def index(request):
    base_template = "default/barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "default/base.html"
    return render_to_response("default/queue.html",
                          {"queue": get_content(request),
                           "base_template": base_template},
                          context_instance=RequestContext(request))
    
@jsonp
@json_wrap
def api(request):
    return [{"time": str(i.time),
             "track": i.songs.track.metadata} for i in get_content(request)]