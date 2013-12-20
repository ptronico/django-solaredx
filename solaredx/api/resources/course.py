# -*- coding: utf-8 -*-

# Django
from django.conf.urls import url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Tastypie
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.bundle import Bundle
from tastypie.resources import Resource

# EDX
from xmodule.modulestore.django import loc_mapper
from xmodule.modulestore.exceptions import ItemNotFoundError

from branding import get_visible_courses
from student.views import course_from_id
from student.models import CourseEnrollment

# SolarEDX
from .utils import Course, mount_course_object_list
from ..forms import ManageCourseUserForm
from ...utils import (course_id_encoder, course_id_decoder, 
    build_lms_absolute_url, build_cms_absolute_url)
    

# Classe Base


class CourseResourceBase(Resource):

    course_id = fields.CharField(attribute='course_id')
    course_absolute_url = fields.CharField(attribute='course_absolute_url')
    course_absolute_url_studio = fields.CharField(
        attribute='course_absolute_url_studio')
    display_name = fields.CharField(attribute='display_name')
    # course_id_solaredx = fields.CharField(attribute='course_id_solaredx')

    start = fields.DateTimeField(attribute='start', null=True)
    end = fields.DateTimeField(attribute='end', null=True)
    enrollment_start = fields.DateTimeField(
        attribute='enrollment_start', null=True)
    enrollment_end = fields.DateTimeField(
        attribute='enrollment_end', null=True)

    class Meta:
        object_class = Course
        detail_uri_name = 'course_id_solaredx'
        # excludes = ['course_id_solaredx']

    def dehydrate(self, bundle):

        print 'api_name:', self._meta.api_name
        print 'resource_name:', self._meta.resource_name

        resource_uri = bundle.data['resource_uri']
        bundle.data['staff_resource_uri'] = '%sstaff/' % resource_uri
        bundle.data['instructor_resource_uri'] = '%sinstructor/' % resource_uri
        return bundle        

    def alter_list_data_to_serialize(self, request, data):
        if 'objects' in data:
            for objects in data['objects']:
                if 'staff_resource_uri' in objects.data:
                    del objects.data['staff_resource_uri']
                if 'instructor_resource_uri' in objects.data:
                    del objects.data['instructor_resource_uri']
        return data
 
    def alter_detail_data_to_serialize(self, request, data):
        if 'resource_uri' in data.data:
            del data.data['resource_uri']
        return data

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)
    
    def obj_get(self, bundle, **kwargs):
        for obj in self.get_object_list(bundle.request):
            if obj.course_id_solaredx == kwargs[self._meta.detail_uri_name]:
                break
        return obj

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


# Classes Filhas


class CourseResource(CourseResourceBase):

    def get_object_list(self, request):
        return mount_course_object_list(get_visible_courses())

    # Adding custom endpoint

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/' \
                '(?P<instructor_or_staff>(staff|instructor))%s$' % (
                self._meta.resource_name, trailing_slash()), 
                self.wrap_view('manage_user'), 
                name="api_manage_user"
            ),
        ]

    def manage_user(self, request, **kwargs):

        # self.method_check(request, allowed=['post'])
        # self.is_authenticated(request)
        # self.throttle_check(request)

        course_id = course_id_decoder(kwargs['pk'])
        instructor_or_staff = kwargs['instructor_or_staff']

        if request.method == 'GET':
            # Retornando lista de usuários 'instructor_or_staff' do curso

            from .user import UserResource
            from django.http import HttpRequest, QueryDict

            new_request = HttpRequest()
            new_request.GET = QueryDict('groups__name=%s_%s' % (
                instructor_or_staff, course_id))
            print new_request

            return UserResource().get_list(new_request)

        if request.method == 'POST':
            # Adicionando/removendo usuário como 'instructor_or_staff'
            
            form = ManageCourseUserForm(request.POST)
            if form.is_valid():

                from .user import UserResource

                action, user = form.update(course_id, instructor_or_staff)

                return UserResource().get_detail(
                    request, username=user.username)

            else:
                return self.create_response(request, { 'status': 'error' })


class UserCourseResource(CourseResourceBase):

    def __init__(self, *args, **kwargs):
        self._current_user = kwargs.pop('user')
        super(UserCourseResource, self).__init__(*args, **kwargs)


    def dehydrate(self, bundle):
        bundle.data['resource_uri'] = reverse('api_dispatch_detail', 
            kwargs={ 'api_name': CourseResource._meta.api_name, 
            'resource_name': CourseResource._meta.resource_name, 
            'course_id_solaredx': course_id_encoder(bundle.data['course_id'])})
        return bundle    

    def get_object_list(self, request):
        
        course_list = []
        user = self._current_user

        # Ref: 'student.views.dashboard'
        for enrollment in CourseEnrollment.enrollments_for_user(user):
            try:
                course_list.append(course_from_id(enrollment.course_id))
            except ItemNotFoundError:
                pass

        return mount_course_object_list(course_list)

    def detail_uri_kwargs(self, bundle_or_obj):
        """ Semelhante ao mesmo método no `ModelResource`. """
        
        kwargs = {}

        print self._meta.detail_uri_name

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = getattr(
                bundle_or_obj.obj, self._meta.detail_uri_name)
        else:
            kwargs[self._meta.detail_uri_name] = getattr(
                bundle_or_obj, self._meta.detail_uri_name)

        return kwargs
