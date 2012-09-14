from django.shortcuts import render_to_response
from ..models import Queue
from django.template.context import RequestContext
from django.http import HttpResponse
import json
from ..tools import jsonp

def index(request):
    base_template = "default/barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "default/base.html"
    return render_to_response("default/queue.html",
                          {"queue": Queue.objects.select_related(),
                           "base_template": base_template},
                          context_instance=RequestContext(request))
    
@jsonp
def api(request):
    return HttpResponse(json.dumps(list(Queue.objects.all())), content_type="application/json")