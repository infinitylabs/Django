from django.contrib import admin
from radio_project import models as m

class DjsAdmin(admin.ModelAdmin):
    pass
admin.site.register(m.Djs, DjsAdmin)