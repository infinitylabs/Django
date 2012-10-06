from django.template.loader import BaseLoader
from models import Theme, Types, Files
from django.template.base import TemplateDoesNotExist
import re

class ThemeLoader(BaseLoader):
    is_usable = True
    
    theme_syntax = re.compile(r'<theme(:|(:(?P<theme>.+?)))?>(?P<filename>.*)')
    def load_template_source(self, template_name, template_dirs=None):
        match = self.theme_syntax.match(template_name)
        if match:
            groups = match.groupdict()
            filename = groups['filename']
            if groups['theme']:
                try:
                    theme = Theme.objects.get(name=groups['theme'])
                except Theme.DoesNotExist:
                    try:
                        theme = Theme.objects.filter(current=True)[0]
                    except IndexError:
                        theme = Theme.objects.get(name="default")
            else:
                try:
                    theme = Theme.objects.filter(current=True)[0]
                except IndexError:
                    theme = Theme.objects.get(name="default")
            for template in theme.files_set.filter(type__type='te'):
                print "And we are in here", filename, template.filename
                if template.filename.strip('/') == filename.strip('/'):
                    # Good we found our template do your shit
                    with open(template.filepath, 'r') as f:
                        print "Why did this fail again"
                        return (f.read(), template.filepath)
            raise TemplateDoesNotExist("Welcome to a crappy template loader.")
        else:
            raise TemplateDoesNotExist("Didn't ask for a theme")