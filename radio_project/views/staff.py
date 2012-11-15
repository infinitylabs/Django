from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from ..models import Dj
from ..api import Api

def index(request):
    base_template = "<theme>barebone.html" if \
            request.GET.get("barebone", False) else \
            "<theme>base.html"
    return render_to_response("<theme>staff.html",
                              {"objects": Dj.objects.filter(visible=1).order_by('priority'),
                               "base_template": base_template},
                              context_instance=RequestContext(request))
    
@Api(default="jsonp")
def api(request):
    return [{"name": i.name,
            "description": i.description,
            "image": i.image} for i in \
                Dj.objects.filter(visible=1).order_by('priority').only("name", "description", "image")]
