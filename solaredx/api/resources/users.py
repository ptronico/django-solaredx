# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from tastypie import fields
from tastypie.resources import ModelResource

from student.models import UserProfile, CourseEnrollment

from ...utils import course_id_encoder


class CourseEnrollmentResource(ModelResource):    

    course_id_solaredx = fields.CharField(attribute='course_id_solaredx', 
        null=True)

    class Meta:
        queryset = CourseEnrollment.objects.all()
        include_resource_uri = False

    def dehydrate(self, bundle):
        bundle.data['course_id_solaredx'] = course_id_encoder(
            bundle.data['course_id'])
        return bundle


class UserProfileResource(ModelResource):    
    class Meta:
        queryset = UserProfile.objects.all()


class UserResource(ModelResource):
    
    profile = fields.ForeignKey(UserProfileResource, 'profile', full=True)
    course_enrollment = fields.ManyToManyField(CourseEnrollmentResource, 
        'courseenrollment_set', full=True, use_in=['detail'])
    
    class Meta:
        queryset = User.objects.all()
        fields = ['id', 'username', 'email', 'date_joined', 
            'is_staff', 'is_active', 'resource_uri']

    def alter_list_data_to_serialize(self, request, data):
        if 'objects' in data:
            for objects in data['objects']:
                if 'profile' in objects.data:
                    del objects.data['profile']
                if 'course_enrollment' in objects.data:
                    del objects.data['course_enrollment']
        return data
