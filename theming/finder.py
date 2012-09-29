from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from models import Theme, Types, Files
import os.path
from django.utils.datastructures import SortedDict

class ThemeStorage(FileSystemStorage):
    pass

class StaticFinder(BaseFinder):
    storage_class = ThemeStorage
    def __init__(self, apps=None, *args, **kwargs):
        self.themes = []
        self.storages = SortedDict()
        for theme in Theme.objects.all():
            theme_storage = self.storage_class(theme.location)
            self.storages[theme] = theme_storage
            if theme not in self.themes:
                self.themes.append(theme)
                
    def find(self, path, all=False):
        matches = []
        for file in Files.objects.filter(type__type='st'):
            filename = file.relative_filename
            print filename
            if os.path.abspath(filename) == os.path.abspath(path):
                if not all:
                    return self.storages[file.theme].path(filename)
                matches.append(self.storages[file.theme].path(filename))
        return matches
                
    def list(self, ignore_patterns):
        for file in Files.objects.filter(type__type='st'):
            yield (file.relative_filename, self.storages[file.theme])