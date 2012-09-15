from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ..models import Streamstatus, Played, Queue, News, Radvars

def collect_data():
    return {}

def index(request):
    base_template = "default/barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "default/base.html"
    np = Streamstatus.objects.all().select_related()
    lp = Played.objects.all().select_related("songs", "songs__track").order_by("-time")[:5]
    queue = Queue.objects.all().select_related("songs", "songs__track").order_by("time")[:5]
    thread = Radvars.objects.get(name='curthread').value
    news = News.objects.all().select_related().order_by('-time')[:3]
    if u'http://' not in thread:
        thread = None
    return render_to_response("default/home.html",
                              {'base_template':base_template,
                               'now_playing': np[0].songs.track.metadata if\
                               len(np) > 0 else 'STREAM IS CURRENTLY DOWN',
                               'listeners': np[0].listener_count if\
                               len(np) > 0 else 0,
                               'dj': np[0].djs if\
                               len(np) > 0 else {'name':'None',
                                                 'description':'No DJ',
                                                 'image':'none.png'},
                               'last_played': lp,
                               'queue': queue,
                               'thread_message': thread,
                               'news': news},
                              context_instance=RequestContext(request))