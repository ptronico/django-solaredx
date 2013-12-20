# -*- coding: utf-8 -*-

from tastypie import utils, fields
from tastypie.resources import Resource


class PingResource(Resource):

    utc_time = fields.DateTimeField(readonly=True, default=utils.now,
        help_text='UTC time returned by our server.')

    class Meta:
        limit = 1
        include_resource_uri = False
        list_allowed_methods = []
        detail_allowed_methods = ['get']
 
    def obj_get(self, bundle, **kwargs):
        return [utils.now]        
 
    def obj_get_list(self, bundle, **kwargs):
        return [utils.now]

    def get_object_list(self, request):
        return [utils.now]

    def dispatch(self, request_type, request, **kwargs):
        # Force this to be a single object (not a list of them)
        return super(PingResource, self).dispatch('detail', request, **kwargs)