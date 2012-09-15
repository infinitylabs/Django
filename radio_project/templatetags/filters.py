from django import template
from radio_project import tools

register = template.Library()

@register.filter
def lptimeformat(value, arg):
    """Formats a datetime object for the Last Played page"""
    return tools.lp_time_format(value)

@register.filter
def qtimeformat(value, arg):
    """Formats a datetime object for the Queue page"""
    return tools.queue_time_format(value)

@register.filter
def searchtimeformat(value, arg):
    """Formats a datetime object for the Search page"""
    return tools.search_time_format(value)

