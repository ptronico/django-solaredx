# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, url, include

from tastypie.api import Api

from .api.resources.ping import PingResource
from .api.resources.users import UserResource, UserProfileResource


dev_api = Api(api_name='dev')
dev_api.register(PingResource())
dev_api.register(UserResource())


test_urls = patterns('solaredx.views',
    url(r'^ping/$', 'ping', name='ping'),
)

urlpatterns = patterns('',
    url(r'^api/', include(test_urls, namespace='solaredx', app_name='solaredx')),
    url(r'^api/', include(dev_api.urls)),
)

# Solução para utilização do Django Debug Toolbar
if settings.DEBUG:
    urlpatterns += patterns('solaredx.views', 
        url(r'^api/debug/', 'debug'),
    )