from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ..models import Streamstatus, Played, Queue, News, Radvars
from ..api import Api

class NP(object):
    """Simple wrapper class for the NP info
    
    adds support for serialization"""
    serialize_hint = {"track": "track",
                      #"favecount": "favecount",
                      #"playcount": "playcount",
                      "listeners": "listeners",
                      "dj": "dj",
                      }
    def __init__(self):
        super(NP, self).__init__()
        try:
            self.streamstatus = Streamstatus.objects.select_related("track", "dj")[0]
        except (Streamstatus.DoesNotExist, IndexError):
            self.streamstatus = None
    @property
    def track(self):
        if self.streamstatus:
            return self.streamstatus.track.metadata
        else:
            return u"STREAM IS CURRENTLY DOWN"
    @property
    def dj(self):
        if self.streamstatus:
            return self.streamstatus.dj
        else:
            return {'name': u'None', 'description': u'No DJ', 'image': u'none.png'}
    @property
    def listeners(self):
        if self.streamstatus:
            return self.streamstatus.listener_count
        else:
            return 0
        
    def __repr__(self):
        return self.track
        
def get_content(request, context):
    # Now playing info, Listeners info, DJ info
    context['now_playing'] = NP()
    # Last played info
    context["last_played"] = Played.objects.all().select_related("song", "song__track").order_by("-time")[:5]
    # Queue info
    context["queue"] = Queue.objects.all().select_related("song", "song__track").order_by("time")[:5]
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
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    context = {'base_template': base_template}
    
    get_content(request, context)

    return render_to_response("<theme>home.html", context,
                              context_instance=RequestContext(request))
    
@Api(default='jsonp')
def api(request):
    return get_content(request, {})
    