# -*- coding: utf-8 -*-

from django.db.models import Count
from django.core.urlresolvers import reverse, NoReverseMatch

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import Resource, ModelResource
from tastypie.exceptions import NotFound

from branding import get_visible_courses
from student.models import CourseEnrollment
from xmodule.modulestore.django import loc_mapper

from ...utils import course_id_encoder


class Course(object):
    """
    Course object, a mix of RDBMS fields (course_id) with NoSQL fields (name).
    """

    course_id = ''
    course_uri = ''
    studio_uri = ''
    display_name = ''

    @property
    def course_id_solaredx(self):
        return course_id_encoder(self.course_id)


class CourseResource(Resource):

    course_id = fields.CharField(attribute='course_id')
    course_uri = fields.CharField(attribute='course_uri')
    studio_uri = fields.CharField(attribute='studio_uri')
    display_name = fields.CharField(attribute='display_name')
    course_id_solaredx = fields.CharField(attribute='course_id_solaredx')

    class Meta:
        object_class = Course
        detail_uri_name = 'course_id_solaredx'


    def get_object_list(self, request):

        object_list = []

        for course in get_visible_courses():

            course_loc = loc_mapper().translate_location(
                course.location.course_id, course.location, 
                published=False, add_entry_if_missing=True)

            c = Course()

            c.course_id = course.id
            c.course_uri = '/courses/%s/about/' % course.id
            c.studio_uri = course_loc.url_reverse('course/', '')
            c.display_name = course.display_name
            
            object_list.append(c)

        return object_list
 
    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        for obj in self.get_object_list(bundle.request):
            if obj.course_id_solaredx == kwargs[self._meta.detail_uri_name]:
                break
        return obj

    # URL-related methods.

    def detail_uri_kwargs(self, bundle_or_obj):
        """ Semelhante ao mesmo método no `ModelResource`. """
        
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = getattr(
                bundle_or_obj.obj, self._meta.detail_uri_name)
        else:
            kwargs[self._meta.detail_uri_name] = getattr(
                bundle_or_obj, self._meta.detail_uri_name)

        return kwargs