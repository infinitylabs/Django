from django.http import HttpResponse
from django.shortcuts import render_to_response
from ..tools import Paginator, Link
from ..models import Played, Songs
from ..api import Api
from django.template.context import RequestContext

def get_content(request):
    paginator = Paginator(Played.objects.order_by("-time")\
          .select_related("song"), 20)
    return paginator.get_context(request.GET.get('page', 1))

def index(request):
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    page = get_content(request)
    
    # Still using a Link due to changes soon
    objects = [Link(songs=i.song, played=i) for i in page['objects']]    
    return render_to_response("<theme>lastplayed.html",
                              {"lastplayed": objects,
                               "base_template": base_template,
                               "page": page},
                              context_instance=RequestContext(request))
@Api(default="jsonp")
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