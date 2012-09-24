"""Various tool found through our journey!"""
from django.http import HttpResponse
from functools import wraps
import json
from django.db.models.query import QuerySet
from django.conf import settings
from datetime import datetime
from time import mktime
import contextlib
import string
import os.path
import random

def filename_generator(extension, size=15, chars=string.letters + string.digits):
    return os.path.join(settings.MUSIC_ROOT, ''.join(random.choice(chars) for x in xrange(size)) + extension)

def get_filename(file):
    extension = os.path.splitext(file.name)[1]
    filename = filename_generator(extension)
    while os.path.isfile(filename):
        filename = filename_generator(extension)
    return filename
 
def lp_time_format(date):
    """Formats a datetime.datetime object into a time for the Last Played page"""
    import datetime
    now = datetime.datetime.now()
    delta = now - date
    if delta.days >= 1:
        return "{days} day{s} ago".format(days=delta.days, s=('' if delta.days == 1 else 's'))
    else:
        return date.strftime('%H:%M:%S')

def queue_time_format(date):
    """Formats a datetime.datetime object into a time for the Queue page"""
    return date.strftime('%H:%M:%S')

def search_time_format(date):
    """Formats a datetime.datetime object into a time for the Search page"""
    if date is None:
        return u'Never'
    return date.strftime('%a %d %b, %H:%M')

from django.core.paginator import InvalidPage, Paginator as _Paginator
class Paginator(_Paginator):
    def get_context(self, page, range_gap=5):
        try:
            page = int(page)
        except (ValueError, TypeError) as err:
            raise InvalidPage, err
        
        paginator = self.page(page)
        
        if page > 5:
            start = page - range_gap
        else:
            start = 1
            
        if page < self.num_pages - range_gap:
            end = page + range_gap + 1
        else:
            end = self.num_pages + 1
            
        context = {
           "page_range": range(start, end),
           "objects": paginator.object_list,
           "num_pages": self.num_pages,
           "page": page,
           "has_pages": self.num_pages > 1,
           "has_previous": paginator.has_previous(),
           "has_next": paginator.has_next(),
           "previous_page": paginator.previous_page_number(),
           "next_page": paginator.next_page_number(),
           "is_first": page == 1,
           "is_last": page == self.num_pages,
           }
        return context
    
class Link(object):
    """Simple class that collects the multiple objects into it
    Does not accept positional arguments
    
    NOTE ABOUT __nonzero__:
        The current one loops over all the items linked, and checks their
        boolean value. If any of them return True the whole Link object will
        be seen as True.
        
    Usage:
        >>> l = Link(magic="World", hello="Hello")
        >>> l.magic
        "World"
        >>> l.hello
        "Hello"
    """
    def __init__(self, **kwargs):
        super(Link, self).__init__()
        self._items = []
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
            self._items.append(value)
    def __nonzero__(self):
        for items in self._items:
            if items:
                return True
        return Fals