from models import Theme, Files, Types

class CollectionObject(object):
    def __init__(self, manager, theme, type):
        super(CollectionObject, self).__init__()
        self.type = None
        self.manager = manager
        self.theme = theme
        try:
            self.type = Types.objects.get(name=type)
        except Types.DoesNotExist:
            manager.exception(u"Selected type '{:s}' does not exist.".format(type))
        
    def __iter__(self):
        if self.type:
            return iter(self.type.files_set.filter(theme=self.theme))
        else:
            return iter([])
    
class TypesObject(object):
    def __init__(self, manager, theme):
        super(TypesObject, self).__init__()
        self.manager = manager
        self.theme = theme
        
    def __getattr__(self, key):
        return CollectionObject(self.manager, self.theme, type=key)
        
    def __repr__(self):
        return repr(self.theme)
    
class ThemeManager(object):
    def __init__(self, user_theme=u"current"):
        super(ThemeManager, self).__init__()
        self.exceptions = ThemeExceptions(self)
        self.user_theme = user_theme
        self._cache = {}
        
    def get_theme(self, name='default'):
        if (name == 'current') and (self.user_theme != 'current'):
            return self.get_theme(self.user_theme)
        elif (name == 'current'):
            try:
                return Theme.objects.get(current=True)
            except Theme.DoesNotExist:
                self.exception(u"No theme selected as 'current'.")
                return self.get_theme('default')
        try:
            return Theme.objects.get(name=name)
        except Theme.DoesNotExist:
            self.exception(
                u"Selected theme '{theme:s}' does not exist.".format(theme=name), 0
                )
            return self.get_theme(name='current')
            
    def exception(self, *args, **kwargs):
        """Shortcut to `manager.exceptions.exception`"""
        self.exceptions.exception(*args, **kwargs)
        
    def __getattribute__(self, key):
        try:
            return super(ThemeManager, self).__getattribute__(key)
        except AttributeError:
            if key not in self._cache:
                self._cache[key] = TypesObject(self, self.get_theme(name=key))
            return self._cache[key]
    
class ThemeExceptions(object):
    """Exception collection, all exceptions in the theming context should be
    appended to this collection rather than being raised towards the template
    processor. The template creator can then decide what to do with these
    because of the fallbacks in the theming"""
    
    def __init__(self, manager):
        super(ThemeExceptions, self).__init__()
        self.manager = manager
        self._internal = []
        
    def exception(self, errmsg, errno=0):
        self.append(ThemeError(errmsg, errno))
        
    def append(self, error):
        self._internal.append(error)
        
    def count(self):
        return len(self)
    
    def __len__(self):
        return len(self._internal)
    
    def __iter__(self):
        return iter(self._internal)
    
    def __repr__(self):
        return "<ThemeExceptions: {errcount:d} errors occured.>".format(errcount=len(self))

class ThemeError(Exception):
    def __init__(self, errmsg=u"Theming error", errno=0):
        super(ThemeError, self).__init__()
        self.errmsg = errmsg
        self.errno = errno
    def __repr__(self):
        return "{message:s} ({errno:d})".format(message=self.errmsg,
                                                errno=self.errno)
        