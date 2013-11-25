# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from tastypie import fields

from student.models import UserProfile, CourseEnrollment


class CourseEnrollmentResource(ModelResource):
    class Meta:
        queryset = CourseEnrollment.objects.all()


class UserProfileResource(ModelResource):    
    class Meta:
        queryset = UserProfile.objects.all()


class UserResource(ModelResource):
    
    profile = fields.ForeignKey(UserProfileResource, 'profile', full=True)
    course_enrollment = fields.ManyToManyField(CourseEnrollmentResource, 
        'courseenrollment_set', full=True, use_in=['detail'])
    
    class Meta:
        queryset = User.objects.all()
        fields = ['id', 'username', 'email', 'date_joined', 'is_active', 
            'resource_uri']

    def alter_list_data_to_serialize(self, request, data):
        if 'objects' in data:
            for objects in data['objects']:
                if 'profile' in objects.data:
                    del objects.data['profile']
                if 'course_enrollment' in objects.data:
                    del objects.data['course_enrollment']
        return data
