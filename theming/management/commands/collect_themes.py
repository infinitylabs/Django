from django.core.management.base import CommandError, NoArgsCommand
from django.conf import settings
from theming.models import Theme
import importlib
import sys
import os

def collect_themes(self, includes, options):
    """Very safe function, doesn't throw exceptions? why"""
    verbosity = options.get('verbosity', 1)
    for directory in includes:
        sys.path.append(directory)
        try:
            potential_module_list = os.walk(directory).next()[1]
        except StopIteration:
            if verbosity > 0:
                self.stdout.write("Included directory '{0}' does not exist\n".format(directory))
            continue
        for potential_theme in potential_module_list:
            location = os.path.join(directory, potential_theme)
            try:
                # We just try importing them, should be more safe maybe?
                theme = importlib.import_module(potential_theme)
            except ImportError:
                # Need to make this more specific assuming it isn't a module right now
                continue
            else:
                if not hasattr(theme, 'files'):
                    if verbosity > 0:
                        self.stdout.write("Expected '{0}' to be a theme, misses 'files' attribute.\n".format(potential_theme))
                    continue
                theme_object, created = Theme.objects.get_or_create(name=potential_theme,
                                     location=location)
                if not created:
                    theme_object.files_set.all().delete()
                    theme_object.delete()
                    theme_object = Theme(name=potential_theme,
                                         location=location)
                theme_object.save()
                theme_object.extend(theme.files)
                if verbosity > 0:
                    self.stdout.write("Found theme '{0}'.\n".format(theme_object))
                    
class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        includes = []
        for app in settings.INSTALLED_APPS:
            try:
                app = importlib.import_module(app)
            except ImportError:
                pass
            else:
                theme_dir = os.path.join(os.path.dirname(app.__file__), "themes")
                includes.append(theme_dir)
        collect_themes(self, includes, options=options)
        # We know everything about our themes now... except the files aren't
        # moved. Maybe we can use a template finder?'