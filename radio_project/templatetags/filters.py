from django import template
from radio_project import tools

register = template.Library()

@register.filter
def lptimeformat(value):
    """Formats a datetime object for the Last Played page"""
    return tools.lp_time_format(value)

@register.filter
def qtimeformat(value):
    """Formats a datetime object for the Queue page"""
    return tools.queue_time_format(value)

@register.filter
def searchtimeformat(value):
    """Formats a datetime object for the Search page"""
    return tools.search_time_format(value)

@register.filter
def newsformat(value, arg=None):
    """Formats a news post string with line breaks and truncation (if needed)
    Argument: truncate - truncates the string at the TRUNCATE mark
    """
    value = value.replace('\n', '<br>')
    if 'TRUNCATE' in value:
        if arg == 'truncate':
            value = value[:value.index('TRUNCATE')]
        value = value.replace('TRUNCATE', '')
    return value
   
@register.filter
def commentformat(value):
    """Formats a comment with line breaks."""
    value = value.replace('\n', '<br>', 10)
    return value