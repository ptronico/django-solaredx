# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse


def ping(request):
    return HttpResponse(json.dumps('pong'), content_type='application/json')