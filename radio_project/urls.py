from django.conf.urls.defaults import *

"""We keep all our URLs in a single file, however do keep each section
seperate please"""

urlpatterns = patterns('radio_project.views.home',
    url(r"^$", "index"),
    url(r"^api/$", "api"),
    )

urlpatterns += patterns('radio_project.views.news',
    url(r"^news/$", "index"),
    url(r"^api/news/$", "api"),
    )

urlpatterns += patterns('radio_project.views.lastplayed',
    url(r"^lastplayed/$", "index"),
    url(r"^api/lastplayed/$", "api"),
    )

urlpatterns += patterns('radio_project.views.queue',
    url(r"^queue/$", "index"),
    url(r"^api/queue/$", "api"),
    )

urlpatterns += patterns('radio_project.views.faves',
    url(r"^faves/$", "index"),
    url(r"^api/faves/$", "api"),
    )

urlpatterns += patterns('radio_project.views.submit',
    url(r"^submit/$", "index"),
    )

urlpatterns += patterns('radio_project.views.staff',
    url(r"^staff/$", "index"),
    url(r"^api/staff/$", "api"),
    )

urlpatterns += patterns('radio_project.views.irc',
    url(r"^irc/$", "index"),
    )

urlpatterns += patterns('radio_project.views.search',
    url(r"^search/$", "index"),
    url(r"^api/search/$", "api"),
    )

urlpatterns += patterns('radio_project.views.request',
    url(r"^api/request/$", "api"),
    )