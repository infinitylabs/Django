from django.contrib import admin
from radio_project import models as m

class DjAdmin(admin.ModelAdmin):
    pass
admin.site.register(m.Dj, DjAdmin)