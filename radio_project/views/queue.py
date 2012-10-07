from django.shortcuts import render_to_response
from ..models import Queue
from django.template.context import RequestContext
from django.http import HttpResponse
from ..api import Api

def get_content(request):
    return Queue.objects.only("track", "time")

def index(request):
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    return render_to_response("<theme>queue.html",
                          {"queue": get_content(request),
                           "base_template": base_template},
                          context_instance=RequestContext(request))
    
@Api(default="jsonp")
def api(request):
    return get_content(request)