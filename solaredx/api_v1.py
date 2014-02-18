# -*- coding: utf-8 -*-

# Django
from django.conf.urls import url
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

# Tastypie
from tastypie import http, fields
from tastypie.bundle import Bundle
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from tastypie.validation import CleanedDataFormValidation
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse

# EDX
from xmodule.modulestore.exceptions import ItemNotFoundError
from branding import get_visible_courses
from student.views import course_from_id
from student.models import CourseEnrollment

# SolarEDX
from .edx import (user_create, user_update, user_delete, 
    user_enroll, user_unenroll, course_create, course_delete, 
    course_add_user, course_remove_user)
from .forms import (UserCreateForm, UserUpdateForm, UserDeleteForm, 
    CourseCreateForm, CourseDeleteForm, UserEnrollForm, UserUnenrollForm,
    CourseAddUserForm, CourseDeleteUserForm)
from .utils import (Course, mount_course_object_list, 
    course_id_encoder, course_id_decoder)


class GroupResource(ModelResource):

    class Meta:
        queryset = Group.objects.all()
        filtering = { 'name': ALL }


# -----------------------------------------------------------------------------
#    UserResource
# -----------------------------------------------------------------------------


class UserResource(ModelResource):

    name = fields.CharField(attribute='name', null=True)
    groups = fields.ManyToManyField(GroupResource, 'groups', null=True)
    
    class Meta:
        queryset = User.objects.select_related('profile').all()
        fields = ['username', 'email', 'date_joined', 'resource_uri']
        detail_uri_name = 'username'
        authorization = Authorization()

        filtering = {
            'username': ALL,
            'email': ALL,
            'date_joined': ALL,
            'groups': ALL_WITH_RELATIONS,
            'username': ALL_WITH_RELATIONS,
        }


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
                if 'profile' in objects.data:
                    del objects.data['profile']
                if 'course_resource_uri' in objects.data:
                    del objects.data['course_resource_uri']
        return data
 
    def alter_detail_data_to_serialize(self, request, data):
        if 'groups' in data.data:
            del data.data['groups']
        if 'resource_uri' in data.data:
            del data.data['resource_uri']
        return data         

    def post_list(self, request, **kwargs):
        """
        Processa requisições POST, para criação de novos usuários.
        """

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        # Desserializando JSON
        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)

        # Construindo bundle
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)

        # Inserindo classe de validação
        self._meta.validation = CleanedDataFormValidation(
            form_class=UserCreateForm)

        # Efetuando validação dos dados
        self.is_valid(bundle)
        
        # Cancelando a operação se houverem erros durante a validação
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, bundle.errors['user']))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        # Criando usuário
        user_create(bundle.data)

        # Adicionando ``resource_uri``
        bundle.data['resource_uri'] = reverse('api_dispatch_detail', 
            kwargs={ 'api_name': UserResource._meta.api_name,
            'resource_name': UserResource._meta.resource_name, 
            'username': bundle.data['username'] })        

        return self.create_response(request, bundle, 
            response_class=http.HttpCreated)

    def patch_detail(self, request, **kwargs):
        """
        Processa requisição PATCH, para modificação do usuário em questão.
        """

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)
        self._meta.validation = CleanedDataFormValidation(
            form_class=UserUpdateForm)
        self.is_valid(bundle)
        
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, bundle.errors['user']))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        user_update(username=kwargs['username'], data=bundle.data)


        return self.create_response(request, bundle, 
            response_class=http.HttpAccepted)

        return http.HttpAccepted()

    def delete_detail(self, request, **kwargs):
        """
        Processa requisição DELETE, para exclusão do usuário em questão.
        """

        # Chamada não permitida
        return http.HttpMethodNotAllowed()

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------        

        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)
        self._meta.validation = CleanedDataFormValidation(
            form_class=UserDeleteForm)
        self.is_valid(bundle)
        
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, bundle.errors))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        user_delete(username=kwargs['username'])
        return http.HttpNoContent()

    # Custom endpoint: /api/v1/{user}/course/
    # ---------------------------------------

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/course%s$" % (
                self._meta.resource_name, trailing_slash()), 
                self.wrap_view('enrollment_dispatch'), 
                name="api_enrollment_dispatch"), # old: update_enrollment
        ]

    def enrollment_dispatch(self, request, **kwargs):
        " Enrollment endpoint proxy. "

        if request.method == 'GET':
            return self._enrollment_get_list(request, **kwargs)
        if request.method == 'POST':
            return self._enrollment_post_list(request, **kwargs)
        elif request.method == 'DELETE':
            return self._enrollment_delete_list(request, **kwargs)
        else:
            return http.HttpMethodNotAllowed()

    def _enrollment_get_list(self, request, **kwargs):
        course_list = []
        for course_enrollment in CourseEnrollment.objects.filter(
            is_active=True, user__username=kwargs['pk']):
            course_list.append(reverse('api_dispatch_detail', kwargs={ 
                'api_name': CourseResource._meta.api_name, 
                'resource_name': CourseResource._meta.resource_name, 
                'course_id_solaredx': course_id_encoder(
                course_enrollment.course_id)}))
        return self.create_response(request, course_list)

    def _enrollment_post_list(self, request, **kwargs):
        " Matricula aluno em curso. "

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)

        # Hack: alterando bundle.data
        bundle.data['username'] = kwargs['pk']

        self._meta.validation = CleanedDataFormValidation(
            form_class=UserEnrollForm)
        self.is_valid(bundle)
        
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, bundle.errors['user']))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        course_id = course_id_decoder(
            bundle.data['course_resource_uri'].split('/')[5])
        user_enroll(kwargs['pk'], course_id)
        del bundle.data['username']
        location = self.get_resource_uri(bundle)
        return self.create_response(request, bundle, 
            response_class=http.HttpCreated, location=location)

    def _enrollment_delete_list(self, request, **kwargs):
        " Desmatricula aluno em curso. "

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = self.build_bundle(
            data=dict_strip_unicode_keys(deserialized), request=request)
        bundle.data['username'] = kwargs['pk']
        self._meta.validation = CleanedDataFormValidation(
            form_class=UserUnenrollForm)
        self.is_valid(bundle)
        
        if bundle.errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, bundle.errors['user']))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------
        
        course_id = course_id_decoder(
            bundle.data['course_resource_uri'].split('/')[5])
        user_unenroll(kwargs['pk'], course_id)
        return http.HttpNoContent()


# -----------------------------------------------------------------------------
#   CourseResourceBase
# -----------------------------------------------------------------------------


class CourseResource(Resource):
    # class CourseResourceBase(Resource):
    # " Classe base de listagem de cursos. "

    course_id = fields.CharField(attribute='course_id')
    course_absolute_url = fields.CharField(attribute='course_absolute_url')
    course_absolute_url_lms = fields.CharField(
        attribute='course_absolute_url_lms')
    course_absolute_url_studio = fields.CharField(
        attribute='course_absolute_url_studio')
    display_name = fields.CharField(attribute='display_name')
    start = fields.DateTimeField(attribute='start', null=True)
    end = fields.DateTimeField(attribute='end', null=True)
    enrollment_start = fields.DateTimeField(
        attribute='enrollment_start', null=True)
    enrollment_end = fields.DateTimeField(
        attribute='enrollment_end', null=True)

    class Meta:
        object_class = Course
        detail_uri_name = 'course_id_solaredx'

    def dehydrate(self, bundle):
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

    # class CourseResource(CourseResourceBase):
    # " Lista todos os cursos disponíveis. "

    def get_object_list(self, request):
        return mount_course_object_list(get_visible_courses())

    def post_list(self, request, **kwargs):        

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = Bundle(data=dict_strip_unicode_keys(deserialized), 
            request=request)
        validation = CleanedDataFormValidation(form_class=CourseCreateForm)
        validation_errors = validation.is_valid(bundle)

        if validation_errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, validation_errors))        

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        course_create(bundle.data)

        # Adicionando ``resource_uri``
        bundle.data['resource_uri'] = reverse('api_dispatch_detail', 
            kwargs={ 'api_name': CourseResource._meta.api_name,
            'resource_name': CourseResource._meta.resource_name, 
            'course_id_solaredx': course_id_encoder(bundle.data['course_id'])})

        return self.create_response(request, bundle, 
            response_class=http.HttpCreated)

    def delete_detail(self, request, **kwargs):
        " Deleta um curso. "

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        course_id = course_id_decoder(kwargs['course_id_solaredx'])
        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = Bundle(data=dict_strip_unicode_keys(deserialized), 
            request=request)
        bundle.data['course_id'] = course_id
        validation = CleanedDataFormValidation(form_class=CourseDeleteForm)
        validation_errors = validation.is_valid(bundle)

        if validation_errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, validation_errors))        

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        course_delete(course_id)
        return http.HttpNoContent()

    # Custom endpoint: /api/v1/{course}/{staff|instructor}/
    # -----------------------------------------------------

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/' \
                r'(?P<staff_or_instructor>\w+)%s$' % (
                self._meta.resource_name, trailing_slash()), 
                self.wrap_view('staff_or_instructor_dispatch'), 
                name="api_staff_or_instructor_dispatch"
            ),
        ]

    def staff_or_instructor_dispatch(self, request, **kwargs):

        staff_or_instructor = kwargs.get('staff_or_instructor', '')

        if staff_or_instructor == 'staff' or \
            staff_or_instructor == 'instructor':

            if request.method == 'GET':
                return self._staff_or_instructor_get_list(request, **kwargs)
            elif request.method == 'POST':
                return self._staff_or_instructor_post_list(request, **kwargs)
            elif request.method == 'DELETE':
                return self._staff_or_instructor_delete_list(request, **kwargs)

        return http.HttpMethodNotAllowed()

    def _staff_or_instructor_get_list(self, request, **kwargs):

        course_id = course_id_decoder(kwargs['pk'])
        staff_or_instructor = kwargs['staff_or_instructor']        
        group_name = '%s_%s' % (staff_or_instructor, course_id)

        user_resource_uri_list = []
        for user in User.objects.filter(groups__name=group_name):
            user_resource_uri_list.append(reverse('api_dispatch_detail', 
                kwargs={ 'api_name': UserResource._meta.api_name,
                'resource_name': UserResource._meta.resource_name, 
                'username': user.username }))

        return self.create_response(request, user_resource_uri_list)

    def _staff_or_instructor_post_list(self, request, **kwargs):

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        course_id = course_id_decoder(kwargs['pk'])
        staff_or_instructor = kwargs['staff_or_instructor']
        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = Bundle(data=dict_strip_unicode_keys(deserialized), 
            request=request)
        
        if 'user_resource_uri' in bundle.data:  
            user_resource_uri = bundle.data['user_resource_uri']
        bundle.data['course_id'] = course_id
        bundle.data['staff_or_instructor'] = kwargs['staff_or_instructor']
        validation = CleanedDataFormValidation(form_class=CourseAddUserForm)
        validation_errors = validation.is_valid(bundle)

        if validation_errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, validation_errors))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        username = user_resource_uri.split('/')[-2:-1][0]
        course_add_user(course_id, username, staff_or_instructor)
        bundle = Bundle(data={ 'user_resource_uri': user_resource_uri }, 
            request=request)
        return self.create_response(request, bundle, 
            response_class=http.HttpCreated)        

    def _staff_or_instructor_delete_list(self, request, **kwargs):

        # ETAPA 1 - Desserialização e validação dos dados recebidos
        # ---------------------------------------------------------

        course_id = course_id_decoder(kwargs['pk'])
        staff_or_instructor = kwargs['staff_or_instructor']
        deserialized = self.deserialize(request, request.body, 
            format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(
            request, deserialized)
        bundle = Bundle(data=dict_strip_unicode_keys(deserialized), 
            request=request)
        
        if 'user_resource_uri' in bundle.data:  
            user_resource_uri = bundle.data['user_resource_uri']
        bundle.data['course_id'] = course_id
        bundle.data['staff_or_instructor'] = kwargs['staff_or_instructor']

        validation = CleanedDataFormValidation(form_class=CourseDeleteUserForm)
        validation_errors = validation.is_valid(bundle)
        
        if validation_errors:
            raise ImmediateHttpResponse(response=self.error_response(
                bundle.request, validation_errors))

        # ETAPA 2 - Efetuando operações no EDX
        # ------------------------------------

        username = user_resource_uri.split('/')[-2:-1][0]
        course_remove_user(course_id, username, staff_or_instructor)
        return http.HttpNoContent()

