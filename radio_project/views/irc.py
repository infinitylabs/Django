from django.shortcuts import render_to_response
from django.template.context import RequestContext
def index(request):
    base_template = "<theme>barebone.html" if \
                    request.GET.get("barebone", False) else \
                    "<theme>base.html"
    return render_to_response("<theme>irc.html",
                          {"base_template": base_template},
                          context_instance=RequestContext(request))