# -*- coding: utf-8 -*-

import json

from django.core import urlresolvers
from django.http import HttpResponse


def ping(request):
    return HttpResponse(json.dumps('pong'), content_type='application/json')


# Solução para utilização do Django Debug Toolbar
# Importante para análise de performance
# http://www.marteinn.se/blog/?p=674
def html_decorator(func):
    def _decorated(*args, **kwargs):
        response = func(*args, **kwargs)
        wrapped = '<html><body>%s</html></body>' % response.content
        # wrapped = ("<html><body>",response.content,"</body></html>")
        return HttpResponse(wrapped)
    return _decorated

@html_decorator
def debug(request):
    path = request.META.get("PATH_INFO")
    api_url = path.replace("debug/", "")
    view = urlresolvers.resolve(api_url)
    accept = request.META.get("HTTP_ACCEPT")
    accept += ",application/json"
    request.META["HTTP_ACCEPT"] = accept
    res = view.func(request, **view.kwargs)
    return HttpResponse(res._container)    