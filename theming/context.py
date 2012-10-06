"""Theming context manager module

    Warning: The naming in this module is confusing. Don't assume anything.
    [1]: ThemeManager-->ThemeObject-->TypesObject
    
    The context is done with the following syntax
    
        theme.(theme_name or 'types').(type or directory).filename
        
    Examples:
        list(theme) = list of all theme names
        list(theme.default) = list of all files in default theme
        list(theme.default.types) = list of all types in default theme
        list(theme.default.css) = list of all css files in default theme
        # The following two examples are the last in resolve order.
        # Having both a directory named 'css' and a type named 'css' will
        # result in the type being selected. Prefix the directory part with
        # __ to make it force directory first. (Really stop making horrible structures already instead)
        theme.default.directory__deep.base_html = file 'directory/deep/base.html'
        theme.default.directory.base_html = file 'directory/base.html'
        
        theme.default.css.base_html = file 'base.html'
        

        """
from models import Theme, Files, Types

class BaseObject(object):
    def __init__(self):
        super(BaseObject, self).__init__()
        self._cache = {}
        self.cache = self._cache
        
    def use_cache(self, key, item=None):
        if item:
            self._cache[key] = item
        else:
            item = self._cache[key]
        return item
    
class TypesObject(object):
    """Object that handles files in the theme tree
    
    Supports iteration to iterate over all files of the specific type this
    object resembles."""
    DoesNotExist = Types.DoesNotExist
    def __init__(self, manager, theme, type):
        super(TypesObject, self).__init__()
        self.type = Types.objects.get(name=type)
        self.manager = manager
        self.theme = theme

    def __getattr__(self, key):
        return Files.objects.filter(theme=self.theme,
                                    type=self.type,
                                    filename__endswith=key)[0]
    def __iter__(self):
        if self.type:
            return iter(self.type.files_set.filter(theme=self.theme))
        else:
            return iter([])
        
class DirObject(object):
    """Object that handles files in the theme directory tree"""
    DoesNotExist = Files.DoesNotExist
    def __init__(self, manager, theme, dir):
        super(DirObject, self).__init__()
        self.dir = dir
        self.manager = manager
        self.theme = theme
        
class ParentObject(object):
    def __init__(self, parents):
        super(ParentObject, self).__init__()
        self._parents = parents
    def __getattribute__(self, key):
        try:
            return super(ParentObject, self).__getattribute__(key)
        except AttributeError:
            for parent in self._parents:
                try:
                    return getattr(parent, key)
                except:
                    pass
            raise
        
class ThemeObject(BaseObject):
    """Second in the theme tree, this object represents a theme.
        
        Supports iteration that returns each type in this specific theme"""
    parents = None
    def __init__(self, manager, theme):
        super(ThemeObject, self).__init__()
        self.manager = manager
        self.theme = theme
        
    @property
    def parent(self):
        """Property that should be used when you want to call a parent of this
        theme. These are defined in the database models"""
        if not self.parents:
            self.parents = (ThemeObject(self.manager, theme) for theme in self.model.extend_set.all())
        return ParentObject(self.parents)
    
    @property
    def model(self):
        return self.theme
    
    def __getattr__(self, key, nocache=False):
        if key in self.cache and not nocache:
            return self.use_cache(key)
        else:
            result = None
            try:
                result = TypesObject(self.manager, self.theme, type=key)
            except TypesObject.DoesNotExist:
                # the thing requested isn't a type?
                try:
                    result = DirObject(self.manager, self.theme, dir=key)
                except DirObject.DoesNotExist:
                    # Not a directory either.
                    if self.parent:
                        return getattr(self.parent, key)
                    else:
                        raise ValueError("Unknown error")
            finally:
                return result
        
    def __repr__(self):
        return repr(self.theme)
    
    def __iter__(self):
        for types in Types.objects.filter(theme=self.theme):
            yield types
            
class ThemeManager(BaseObject):
    """Root theme manager. This is the object contained in the 'theme' name
    in a `RequestContext`. Supports the following:
    
    exception:
        Any exceptions that occur in the theming process and feel like they 
        can't be handled should be handled by calling `ThemeManager.exception`.
        
    exceptions:
        An attribute containing a `ThemeExceptions` class.
    
    get_theme:
        Returns a Theme model instance of the requested theme.
        Defaults to 'default'
        
    The `ThemeManager` class is iterable and will return a generator
    that returns all themes in the database."""
    def __init__(self, user_theme=u"current"):
        super(ThemeManager, self).__init__()
        self.exceptions = ThemeExceptions(self)
        self.user_theme = user_theme
        
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
            if name == 'default':
                raise ThemeError("There is no default theme supplied.")
            return self.get_theme(name='current')
            
    def exception(self, *args, **kwargs):
        """Shortcut to `manager.exceptions.exception`"""
        self.exceptions.exception(*args, **kwargs)
        
    def __getattribute__(self, key):
        try:
            return super(ThemeManager, self).__getattribute__(key)
        except AttributeError:
            if key not in self.cache:
                self.use_cache(key, ThemeObject(self, self.get_theme(name=key)))
            return self.use_cache(key)
        
    def __iter__(self):
        """Iterates over all Theme rows in the database"""
        for theme in Theme.objects.all():
            yield self.use_cache(theme.name, ThemeObject(self, theme))
            
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
        