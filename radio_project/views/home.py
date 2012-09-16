from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ..models import Streamstatus, Played, Queue, News, Radvars
from ..tools import json_wrap, jsonp

def get_content(request, context):
    # Now playing info, Listeners info, DJ info
    try:
        np = Streamstatus.objects.select_related("songs__track", "djs")[0]
        context["now_playing"] = np.songs.track.metadata
        context["listeners"] = np.listener_count
        context["dj"] = np.djs
    except (Streamstatus.DoesNotExist, IndexError):
        context["now_playing"] = u"STREAM IS CURRENTLY DOWN"
        context["listeners"] = 0
        context["dj"] = {'name':u'None', 'description':u'No DJ', 'image':u'none.png'}
    # Last played info
    context["last_played"] = Played.objects.all().select_related("songs", "songs__track").order_by("-time")[:5]
    # Queue info
    context["queue"] = Queue.objects.all().select_related("songs", "songs__track").order_by("time")[:5]
    # Thread info
    try:
        thread = Radvars.objects.get(name=u'curthread').value
    except Radvars.DoesNotExist:
        thread = None
    finally:
        if thread and u'http://' not in thread:
            thread = None
        context["thread"] = thread
        
    # News info
    context["news"] = News.objects.all().select_related().order_by('-time')[:3]
    return context

def index(request):
    base_template = "default/barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "default/base.html"
    context = {'base_template': base_template}
    
    get_content(request, context)

    return render_to_response("default/home.html", context,
                              context_instance=RequestContext(request))
    
@jsonp
@json_wrap({News: ["id", "time", "title", "text"]})
def api(request):
    return get_content(request, {})
    