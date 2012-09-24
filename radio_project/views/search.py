from ..tools import Paginator, jsonp, json_wrap
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from ..search import Searcher
from ..models import Track
from ..api import Api

lastplayed = """SELECT MAX(played.time) FROM played JOIN songs ON
                songs.id = played.songs_id JOIN track AS inner_tracks 
                ON inner_tracks.id = songs.track_id WHERE 
                inner_tracks.id = track.id"""
lastrequested = """SELECT MAX(requests.time) FROM requests JOIN songs ON
                songs.id = requests.songs_id JOIN track AS inner_tracks
                ON inner_tracks.id = songs.track_id WHERE 
                inner_tracks.id = track.id"""
                
def get_content(request):
    query = request.GET.get('query', u'')
    page = request.GET.get('page', 1)
    with Searcher() as searcher:
        query = query + u" NOT kind:track" # Alter query to include only database entries
        # Make a whoosh query
        wquery = searcher.parse(query)
        # Call whoosh, hold on to the QuerySet we need to add extras
        result = searcher.search(wquery, limit=None)
        runtime = result.runtime
        # Add extra subselects
        result = result.extra(select={"lastplayed": lastplayed,
                                      "lastrequested": lastrequested})
        # Pass queryset to Paginator
        paginator = Paginator(result, 20)
    return paginator.get_context(page), runtime

def index(request):
    base_template = "default/barebone.html" if \
        request.GET.get("barebone", False) else \
        "default/base.html"
    page, runtime = get_content(request)
    context = {"page": page,
               "results": page['objects'],
               "base_template": base_template,
               "runtime": runtime}
    return render_to_response("default/search.html", context,
                              context_instance=RequestContext(request))
    
@Api(default="jsonp", serialize_hint={Track: ["metadata", "lastplayed", "lastrequested"]})
def api(request):
    page, runtime = get_content(request)
    return [runtime, [page]]

from time import mktime
def map_track(item):
    return [item.metadata,
            mktime(item.lastplayed.timetuple()) if item.lastplayed else None,
            mktime(item.lastrequested.timetuple()) if item.lastrequested else None]
