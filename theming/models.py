from __future__ import unicode_literals
from django.db import models
from django.conf import settings
import os.path

class Theme(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the Theme")
    live = models.BooleanField(default=True, help_text="Theme usable in live environment.")
    location = models.TextField(blank=False, help_text="Theme root on the filesystem.")
    current = models.BooleanField(default=False, help_text="Denotes if this is the active theme.")
            
    @property
    def filepath(self):
        """Returns the filesystem path to this theme. Use this instead of `location`
        for further changes if any."""
        return self.location
    
    @property
    def webpath(self):
        """Returns the URL that points to this themes directory"""
        return '/'.join([settings.STATIC_URL.rstrip("/"), 'themes', self.name])
    
    def __repr__(self):
        return "<Theme '{name}' with {files:d} files>"\
            .format(name=self.name, files=self.files_set.count())
    def __iter__(self):
        return self.files_set.all()