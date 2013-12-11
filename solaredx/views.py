# -*- coding: utf-8 -*-

import json

from django.core import urlresolvers
from django.shortcuts import HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout

from courseware.courses import get_course
from xmodule.modulestore.django import loc_mapper

from .utils import solaredx_encrypt


@require_POST
@csrf_exempt
def auth_login(request):
    " Faz login do usuário, de acordo com a solicitação do Solar. "
    
    token = request.POST.get('token', '')
    username = request.POST.get('username', '')

    logout(request)
    is_logged = False

    user = authenticate(username=username)

    if user is not None:
        if token == solaredx_encrypt(username):
            login(request, user)
            is_logged = True
    
    next = request.GET.get('next', '/')
    
    if is_logged:
        return redirect(next)
    else:
        return HttpResponse('Invalid username or token.')

def ping(request):
    return HttpResponse(json.dumps('pong'), content_type='application/json')

def test(request):

    c = get_course('UFC/CS101/2013_Fall')
    course_loc = loc_mapper().translate_location(c.location.course_id, 
        c.location, published=False, add_entry_if_missing=True)
    url = course_loc.url_reverse('course/', '')

    return HttpResponse(url)
    # return HttpResponse(urlresolvers.reverse('about_course', args=['UFC/CS101/2013_Fall']))


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