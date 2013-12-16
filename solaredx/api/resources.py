# -*- coding: utf-8 -*-

# Django
from django.conf.urls import url
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# Tastypie
from tastypie import utils, fields
from tastypie.bundle import Bundle
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import NotFound
from tastypie.utils import now, trailing_slash

# EDX
from branding import get_visible_courses
from student.models import UserProfile, CourseEnrollment
from xmodule.modulestore.django import loc_mapper
from course_creators.models import CourseCreator

# SolarEDX
from .forms import CourseEnrollmentUpdateForm
from ..utils import (course_id_encoder, course_id_decoder, 
    build_lms_absolute_url, build_cms_absolute_url)


class CourseEnrollment2(object):

    course_id = ''
    username = ''
    action = ''


class Course(object):
    """
    Course object, a mix of RDBMS fields (course_id) with NoSQL fields (name).
    """

    pk = 1
    staff = 1
    course_id = ''
    course_absolute_url = ''
    course_absolute_url_studio = ''
    display_name = ''
    start = ''
    end = ''
    enrollment_start = ''
    enrollment_end = ''

    @property
    def course_id_solaredx(self):
        return course_id_encoder(self.course_id)



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


### Auth

class AuthResource(Resource):

    token = fields.CharField(attribute='token')
    username = fields.CharField(attribute='username')

    class Meta:
        limit = 1
        include_resource_uri = False
        list_allowed_methods = []
        detail_allowed_methods = ['get']

    def obj_get(self, bundle, **kwargs):
        return []


### Users


class CourseEnrollmentResource(ModelResource):
    """ Esse Resource é responsável pela alocação de alunos em cursos. """

    username = fields.CharField(attribute='username', null=True)

    class Meta:
        queryset = CourseEnrollment.objects.select_related('user').all()
        fields = ['id', 'course_id', 'is_active', 'username']
        include_resource_uri = False
        # detail_allowed_methods = []

        filtering = {
            'user': ALL_WITH_RELATIONS,
            'course_id': ALL_WITH_RELATIONS,
        }


    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.user.username
        return bundle

    def obj_create(self, bundle, **kwargs):
        " Cria um relacionamento aluno-curso. "        

        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        bundle = self.full_hydrate(bundle)

        # Capiturando campos enviados
        course_id = bundle.obj.course_id
        username = bundle.obj.username

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            print 'Criando um relacionamento aluno-curso.'
            # CourseEnrollment.enroll(user, course_id)

            # CourseEnrollment.unenroll(user, course_id)

    def put_detail(self, request, **kwargs):
        " Atualiza o estado de um CourseEnrollment. "

        try:
            ce = CourseEnrollment.objects.get(id=int(kwargs['pk']))
        except CourseEnrollment.DoesNotExist:
            ce = None

        if ce:

            if request.POST.get('is_active', '') == 'true':
                is_active = True
            elif request.POST.get('is_active', '') == 'false':
                is_active = False
            else:
                is_active = None

            if is_active is not None:

                ce.is_active = is_active
                ce.save()

    def obj_delete(self, **kwargs):
        " Remove um relacionamento aluno-curso. "
        print 'Removendo um relacionamento aluno-curso.'
        print kwargs


class UserProfileResource(ModelResource):    
    class Meta:
        queryset = UserProfile.objects.all()


def get_course_for_user_enrollment(bundle):

    course_list = []
    for enrollment in CourseEnrollment.objects.filter(
        user__username=bundle.obj.username):
        
        c = Course()
        c.course_id = enrollment.course_id
        course_list.append(c)

    return course_list


class CourseEnrollment2Resource(Resource):

    username = fields.CharField(attribute='username', null=True)
    course_id = fields.CharField(attribute='course_id', null=True)
    action = fields.CharField(attribute='action', null=True)

    class Meta:
        object_class = CourseEnrollment2
        detail_uri_name = 'course_id_solaredx'
        # excludes = ['course_id_solaredx']


    def alter_list_data_to_serialize(self, request, data):
        # Maneira feia de "excluir" alguns campos (ManyToMany)
        if 'objects' in data:
            for objects in data['objects']:
                if 'staff' in objects.data:
                    del objects.data['staff']
                if 'instructor' in objects.data:
                    del objects.data['instructor']
        return data        


    def get_object_list(self, request):

        object_list = []

        for course in get_visible_courses():

            course_loc = loc_mapper().translate_location(
                course.location.course_id, course.location, 
                published=False, add_entry_if_missing=True)

            c = Course()

            c.course_id = course.id
            c.display_name = course.display_name

            # URLs
            c.course_absolute_url = build_lms_absolute_url('/courses/%s/about' % course.id)
            c.course_absolute_url_studio = build_cms_absolute_url(course_loc.url_reverse('course/', ''))            

            c.start = course.start
            c.end = course.end
            c.enrollment_start = course.enrollment_start
            c.enrollment_end = course.enrollment_end

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


class Course2Resource(ModelResource):
    
    class Meta:
        queryset = CourseEnrollment.objects.all()
        include_resource_uri = True

    def get_resource_uri(self, bundle_or_obj):

        prefix = '/solaredx/api/dev/course/'

        if isinstance(bundle_or_obj, Bundle):
            return '%s%s/' % (prefix, course_id_encoder(bundle_or_obj.obj.course_id))
        else:
            return '%s%s/' % (prefix, course_id_encoder(obj.course_id))


class UserResource(ModelResource):
    
    # profile = fields.ForeignKey(UserProfileResource, 'profile', full=True)

    # course_enrollment = fields.ManyToManyField(CourseEnrollmentResource, 'courseenrollment_set')

    name = fields.CharField(attribute='name', null=True) # Profile.name

    course_enrollment = fields.ManyToManyField('solaredx.api.resources.Course2Resource', 
        attribute=lambda bundle: CourseEnrollment.objects.filter(
        is_active=True, user_id=bundle.obj.id), null=True)
    
    class Meta:
        queryset = User.objects.select_related('profile').all()
        fields = ['username', 'email', 'date_joined', 'is_active', 'resource_uri']
        detail_uri_name = 'username'

        filtering = {
            'username': ALL_WITH_RELATIONS,
        }


    def dehydrate(self, bundle):
        bundle.data['name'] = bundle.obj.profile.name
        return bundle    

    def alter_list_data_to_serialize(self, request, data):
        if 'objects' in data:
            for objects in data['objects']:
                if 'profile' in objects.data:
                    del objects.data['profile']
                if 'course_enrollment' in objects.data:
                    del objects.data['course_enrollment']
        return data            

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/course_enrollment%s$" % (
                self._meta.resource_name, trailing_slash()), 
                self.wrap_view('update_enrollment'), 
                name="api_update_enrollment"),
        ]

    # Custom endpoint

    def update_enrollment(self, request, **kwargs):
        " This endpont implements a transparent `enroll` or `unenroll` action. "

        self.method_check(request, allowed=['post'])
        # self.is_authenticated(request)
        # self.throttle_check(request)        

        form = CourseEnrollmentUpdateForm(request.POST)

        try:
            user = User.objects.get(username=kwargs['pk'])
        except User.DoesNotExist:
            user = None

        if user and form.is_valid():
            form.update_enrollment(user)
            return self.create_response(request, { 'status' : 'success', })
        else:
            return self.create_response(request, { 'status' : 'error', })


# Courses

class StaffGroup(ModelResource):

    course_id = fields.CharField(attribute='course_id', null=True)
    course_id_solaredx = fields.CharField(attribute='course_id_solaredx', null=True)

    user = fields.ManyToManyField(UserResource, attribute=lambda bundle:
        User.objects.filter(groups__id=bundle.obj.id))

    class Meta:
        queryset = Group.objects.filter(name__startswith='staff_')
        # detail_uri_name = 'course_id_solaredx'
        fields = ['id', 'course_id', 'course_id_solaredx']

        filtering = {
            'name': ALL,
        }

    def dehydrate(self, bundle):
        course_id = bundle.obj.name.replace('staff_', '')
        bundle.data['course_id'] = course_id
        bundle.data['course_id_solaredx'] = course_id_encoder(course_id)
        return bundle


class InstructorGroup(ModelResource):
    class Meta:
        queryset = Group.objects.filter(name__startswith='instructor_')        

class CourseResource(Resource):

    course_id = fields.CharField(attribute='course_id')
    course_absolute_url = fields.CharField(attribute='course_absolute_url')
    course_absolute_url_studio = fields.CharField(attribute='course_absolute_url_studio')
    display_name = fields.CharField(attribute='display_name')
    course_id_solaredx = fields.CharField(attribute='course_id_solaredx')

    start = fields.DateTimeField(attribute='start', null=True)
    end = fields.DateTimeField(attribute='end', null=True)
    enrollment_start = fields.DateTimeField(attribute='enrollment_start', null=True)
    enrollment_end = fields.DateTimeField(attribute='enrollment_end', null=True)

    # Related data
    staff = fields.ManyToManyField(UserResource, attribute=lambda bundle: 
        User.objects.filter(groups__name__startswith='staff_%s' % 
        bundle.obj.course_id), null=True, related_name='staff')
    instructor = fields.ManyToManyField(UserResource, attribute=lambda bundle: 
        User.objects.filter(groups__name__startswith='instructor_%s' % 
        bundle.obj.course_id), null=True, related_name='instructor')

    class Meta:
        object_class = Course
        detail_uri_name = 'course_id_solaredx'
        # excludes = ['course_id_solaredx']


    def alter_list_data_to_serialize(self, request, data):
        # Maneira feia de "excluir" alguns campos (ManyToMany)
        if 'objects' in data:
            for objects in data['objects']:
                if 'staff' in objects.data:
                    del objects.data['staff']
                if 'instructor' in objects.data:
                    del objects.data['instructor']
        return data        


    def get_object_list(self, request):

        object_list = []

        for course in get_visible_courses():

            course_loc = loc_mapper().translate_location(
                course.location.course_id, course.location, 
                published=False, add_entry_if_missing=True)

            c = Course()

            c.course_id = course.id
            c.display_name = course.display_name

            # URLs
            c.course_absolute_url = build_lms_absolute_url('/courses/%s/about' % course.id)
            c.course_absolute_url_studio = build_cms_absolute_url(course_loc.url_reverse('course/', ''))            

            c.start = course.start
            c.end = course.end
            c.enrollment_start = course.enrollment_start
            c.enrollment_end = course.enrollment_end

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