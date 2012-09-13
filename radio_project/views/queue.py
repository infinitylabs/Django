from django.shortcuts import render_to_response
from ..models import Queue
from django.template.context import RequestContext
from django.http import HttpResponse
import json
from ..tools import jsonp

def index(request):
    return render_to_response("default/queue.html",
                          {"queue": Queue.objects.all()},
                          context_instance=RequestContext(request))
    
@jsonp
def api(request):
    return HttpResponse(json.dumps(list(Queue.objects.all())), content_type="application/json")