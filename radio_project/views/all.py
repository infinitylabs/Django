from ..api import Api, Clean
from importlib import import_module

api_list = ['faves', 'home', 'lastplayed', 'news', 'queue', 'relay', 'staff']

@Api(default='json')
def api(request):
    original_type = request.GET.get('type', None)
    request.GET = request.GET.copy()
    request.GET['type'] = Clean
    results = {}
    for module_name in api_list:
        try:
            module = import_module('.' + module_name, 'radio_project.views')
        except ImportError:
            pass
        else:
            try:
                results[module_name] = module.api(request)
            except:
                pass
    request.GET['type'] = original_type
    return results