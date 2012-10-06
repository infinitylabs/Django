from __future__ import unicode_literals
from django.db import models
from django.conf import settings
import os.path

class Theme(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the Theme")
    live = models.BooleanField(default=True, help_text="Theme usable in live environment.")
    location = models.TextField(blank=False, help_text="Theme root on the filesystem.")
    current = models.BooleanField(default=False, help_text="Denotes if this is the active theme.")
    inherits = models.ManyToManyField('self', blank=True,
                                    null=True, symmetrical=False)
    
    def append(self, filename, type):
        file = Files(theme=self, filename=filename.strip('/'), type=type)
        file.save()
        
    def extend(self, files):
        """Expects list of tuples to put into `Theme.append`"""
        for filename, directory in files:
            self.append(filename, directory)
            
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

class Types(models.Model):
    """The Type of file the theme file is, used for directory prefixes and the like"""
    name = models.CharField(max_length=100, help_text="Short name for this type.")
    directory = models.CharField(max_length=100, help_text="Directory to place this type in.", default=None, blank=True, null=True)
    type = models.CharField(max_length=2, choices=(('st', 'Static File'), ('te', 'Template File')), default='te')
    def __repr__(self):
        return "<Type '{name:s}'>".format(name=self.name)
    
    @classmethod
    def get(cls, name, type='te', directory=None):
        """Simple helper method to retrieve file types"""
        typ, created = cls.objects.get_or_create(name=name, type=type, defaults={"directory": directory})
        if created:
            typ.save()
        return typ
    
class Files(models.Model):
    """A Theme File, all files used in a Theme are of this type"""
    theme = models.ForeignKey(Theme, help_text="Theme this file is part of.")
    filename = models.TextField(blank=False, help_text="Filename relative to Theme root.")
    type = models.ForeignKey(Types, help_text="Type of file this is.")
    
    @property
    def filepath(self):
        if self.type.directory:
            return os.path.join(self.theme.location, self.type.directory, self.filename)
        else:
            return os.path.join(self.theme.location, self.filename)
    
    @property
    def webpath(self):
        """Returns the URL that points to this file"""
        if self.type.directory:
            return '/'.join([self.theme.webpath.rstrip('/'), self.type.directory, self.filename])
        else:
            return '/'.join([self.theme.webpath.rstrip('/'), self.filename])
    
    @property
    def relative_filename(self):
        if self.type.directory:
            return os.path.join(self.type.directory, os.path.basename(self.filename))
        else:
            return self.filename
        
    def __repr__(self):
        return "<{name:s} File: {location:s}>".format(name=self.type.name, location=self.filepath)
    