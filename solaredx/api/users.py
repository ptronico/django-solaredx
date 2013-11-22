
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
    course_enrollment = fields.ManyToManyField(CourseEnrollmentResource, 'courseenrollment_set', full=True)
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['password', 'is_staff', 'is_superuser']



