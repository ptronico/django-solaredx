
from django.conf.urls import patterns, url, include

from tastypie.api import Api

from .api.users import UserResource, UserProfileResource


dev_api = Api(api_name='dev')
dev_api.register(UserResource())


test_urls = patterns('solaredx.views',
    url(r'^ping/$', 'ping', name='ping'),
)

urlpatterns = patterns('',
    url(r'^api/', include(test_urls, namespace='solaredx', app_name='solaredx')),
    url(r'^api/', include(dev_api.urls)),
)