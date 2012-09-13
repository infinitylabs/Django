from django.shortcuts import render_to_response

def collect_data():
    return {}

def index(request):
    return render_to_response("default/home.html",
                              collect_data(),
                              context_instance=RequestContext(request))