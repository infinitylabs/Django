from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from ..models import Djs
from ..tools import jsonp, json_wrap

def index(request):
    base_template = "default/barebone.html" if \
            request.GET.get("barebone", False) else \
            "default/base.html"
    return render_to_response("default/staff.html",
                              {"objects": Djs.objects.filter(visible=1).order_by('priority'),
                               "base_template": base_template},
                              context_instance=RequestContext(request))
    
@jsonp
@json_wrap
def api(request):
    return [{"name": i.name,
            "description": i.description,
            "image": i.image} for i in \
                Djs.objects.filter(visible=1).order_by('priority').only("name", "description", "image")]
