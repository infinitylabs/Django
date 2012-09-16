from django.http import HttpResponse
from django.shortcuts import render_to_response
from ..tools import Paginator, Link, jsonp, json_wrap
from ..models import Played, Songs
from django.template.context import RequestContext

def get_content(request):
    paginator = Paginator(Played.objects.order_by("-time")\
          .select_related("songs"), 20)
    return paginator.get_context(request.GET.get('page', 1))

def index(request):
    base_template = "default/barebone.html" if \
                request.GET.get("barebone", False) else \
                "default/base.html"
    page = get_content(request)
    
    # Still using a Link due to changes soon
    objects = [Link(songs=i.songs, played=i) for i in page['objects']]    
    return render_to_response("default/lastplayed.html",
                              {"lastplayed": objects,
                               "base_template": base_template,
                               "page": page},
                              context_instance=RequestContext(request))
@jsonp
@json_wrap()
def api(request):
    return get_content(request)['objects']
    
def test(page=None):
    import random
    if not page:
        request.GET.update({"page": random.randrange(1, paginator.num_pages)})
    page = get_content(request)
    
    objects = [Link(songs=i.songs, played=i) for i in page['objects']]
    
    for item in objects:
        item.played.time, item.songs.track.metadata, item.songs.played_set.count(), item.songs.faves_set.count()