from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage
from models import Theme
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
        for theme in Theme.objects.all():
            root_path = theme.location
            for name, dirs, files in os.walk(root_path):
                for file in [f for f in files if not f.endswith('.tmpl')]:
                    if os.path.abspath(os.path.join(name, file)) == os.path.abspath(path):
                        if not all:
                            return self.storages[theme].path(file)
                        matches.append(self.storages[theme].path(file))
        return matches
        
    def list(self, ignore_patterns):
        for theme in Theme.objects.all():
            root_path = theme.location
            for name, dirs, files in os.walk(root_path):
                for file in self.filter_dynamic(files):
                    yield (os.path.join(name, file).lstrip(root_path), self.storages[theme])

    def filter_dynamic(self, files):
        return [f for f in files if not f.endswith('.tmpl')]