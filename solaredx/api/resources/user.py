# -*- coding: utf-8 -*-

# Django
from django.conf.urls import url
from django.contrib.auth.models import User, Group

# Tastypie
from tastypie import http, fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash

# SolarEDX
from ..forms import ManageUserForm, CourseEnrollmentUpdateForm
from ...utils import (course_id_encoder, build_lms_absolute_url, 
    build_cms_absolute_url)


class GroupResource(ModelResource):

    class Meta:
        queryset = Group.objects.all()
        filtering = { 'name': ALL }


class UserResource(ModelResource):

    name = fields.CharField(attribute='name', null=True)
    groups = fields.ManyToManyField(
        'solaredx.api.resources.user.GroupResource', 'groups')
    
    class Meta:
        queryset = User.objects.select_related('profile').all()
        fields = ['username', 'email', 'date_joined', 'resource_uri']
        detail_uri_name = 'username'

        filtering = {
            'is_active': ALL,
            'groups': ALL_WITH_RELATIONS,
            'username': ALL_WITH_RELATIONS,
        }

    def post_list(self, request, **kwargs):
        form = ManageUserForm(request.POST)
        if form.is_valid():
            user = form.update()
            if form.cleaned_data['action'] == 'delete':
                return self.create_response(request, { 'status': 'success' })
            return UserResource().get_detail(request, username=user.username)
        else:
            return self.create_response(request, 
                { 'status': 'error', 'errors': form.errors })

    def dehydrate(self, bundle):
        resource_uri = bundle.data['resource_uri']
        bundle.data['name'] = bundle.obj.profile.name
        bundle.data['course_resource_uri'] = '%scourse/' % resource_uri
        return bundle         

    def alter_list_data_to_serialize(self, request, data):
        if 'objects' in data:
            for objects in data['objects']:
                if 'groups' in objects.data:
                    del objects.data['groups']
                if 'course_resource_uri' in objects.data:
                    del objects.data['course_resource_uri']
        return data
 
    def alter_detail_data_to_serialize(self, request, data):
        if 'groups' in data.data:
            del data.data['groups']
        if 'resource_uri' in data.data:
            del data.data['resource_uri']
        return data   

    # Adding custom endpoint

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/course%s$" % (
                self._meta.resource_name, trailing_slash()), 
                self.wrap_view('update_enrollment'), 
                name="api_update_enrollment"),
        ]

    def update_enrollment(self, request, **kwargs):
        """
        Esse `endpoint` da API implementa duas funcionalidades:

        Se a requisição for GET, lista os cursos em que o usuário 
        está matriculado.

        Se a requisição for POST, matricula/desmatricula o usuário 
        em um curso.
        """

        # self.method_check(request, allowed=['post'])
        # self.is_authenticated(request)
        # self.throttle_check(request)

        try:
            user = User.objects.get(username=kwargs['pk'])
        except User.DoesNotExist:
            return http.HttpNotFound()

        if request.method == 'GET':
            # Retornando cursos em que o usuário está matriculado
            from .course import UserCourseResource
            return UserCourseResource(user=user).get_list(request)

        if request.method == 'POST':
            # Matriculando o usuário em um curso
            form = CourseEnrollmentUpdateForm(request.POST)
            if user and form.is_valid():
                
                from .course import CourseResource

                course = form.update_enrollment(user)

                return CourseResource().get_detail(request, 
                    course_id_solaredx=course_id_encoder(course.id))

            else:
                return self.create_response(request, { 'status': 'error' })

