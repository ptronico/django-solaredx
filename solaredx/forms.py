# -*- coding: utf-8 -*-

# Django
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User, Group

# EDX
from auth.authz import create_all_course_groups
from contentstore.utils import delete_course_and_groups
from contentstore.views.tabs import initialize_course_tabs
from django_comment_common.utils import seed_permissions_roles
# from student.views import course_from_id
from student.models import CourseEnrollment #, UserProfile
from xmodule.html_module import AboutDescriptor
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore.exceptions import InvalidLocationError # ItemNotFoundError, InsufficientSpecificationError

# SolarEDX
from .edx import has_course, is_user_enrolled, CourseValidator
from .utils import course_id_decoder

# COURSE

class CourseCreateForm(forms.Form):

    course_id = forms.CharField(required=True)
    display_name = forms.CharField(required=True)
    course_creator_username = forms.CharField(required=False)

    # Formato: '2014-01-28 10:20:30' / 'Wed, 31 Dec 1969 21:00:00 -0300'
    # end = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])
    # start = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])
    # enrollment_end = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])
    # enrollment_start = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])

    def __init__(self, *args, **kwargs):
        super(CourseCreateForm, self).__init__(*args, **kwargs)

        course_id = self.data['course_id'] \
            if 'course_id' in self.data else None
        display_name = self.data['display_name'] \
            if 'display_name' in self.data else None
        course_creator_username = self.data['course_creator_username'] \
            if 'course_creator_username' in self.data else None

        self.validation = CourseValidator(
            course_id, display_name, course_creator_username)

    def clean_course_id(self):
        " Valida ``course_id``. "
        if self.validation.is_course_id_valid() == False:
            raise forms.ValidationError('Invalid course_id!')
        if self.validation.does_course_exist() == True:
            raise forms.ValidationError('Course object already exists!')
        return self.cleaned_data['course_id']

    def clean_course_creator_username(self):
        " Valida ``course_creator_username``. "
        if self.validation.does_course_creator_exist() == False:
            raise forms.ValidationError('User object does not exist!')
        return self.cleaned_data['course_creator_username']


class CourseDeleteForm(forms.Form):

    confirm = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CourseDeleteForm, self).__init__(*args, **kwargs)
        course_id = self.data['course_id'] \
            if 'course_id' in self.data else None
        self.validation = CourseValidator(course_id)

    def clean_confirm(self):
        if not self.cleaned_data['confirm'] or \
            self.validation.does_course_exist() == False:
            raise forms.ValidationError('This field is false or/and ' \
                'course object does not exists!')
        return self.cleaned_data['confirm']


class CourseAddUserForm(forms.Form):

    course_id = forms.CharField()
    user_resource_uri = forms.CharField()
    staff_or_instructor = forms.CharField()

    def clean_user_resource_uri(self):

        try:
            username = self.cleaned_data['user_resource_uri'].split('/')[-2:-1][0]
        except:
            username = None

        self._user = None
        if username:
            try:
                self._user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass

        if not self._user:
            raise forms.ValidationError('User object not found!')

        return self.cleaned_data

    def clean(self):
        cleaned_data = super(CourseAddUserForm, self).clean()

        try:
            group = Group.objects.get(name='%s_%s' % (
                cleaned_data.get('staff_or_instructor'), 
                cleaned_data.get('course_id')))
        except Group.DoesNotExist:
            group = None

        if group is None:
            msg = '%s group for %s does not exist! Please ' \
                'contact the server admin!' % (
                cleaned_data.get('staff_or_instructor').capitalize(), 
                cleaned_data.get('course_id'))
            self._errors['user_resource_uri'] = self.error_class([msg])
            if 'user_resource_uri' in cleaned_data:
                del cleaned_data['user_resource_uri']
        elif self._user in group.user_set.all():
            msg = "User object already is a/an '%s'." % cleaned_data.get(
                'staff_or_instructor')
            self._errors['user_resource_uri'] = self.error_class([msg])
            if 'user_resource_uri' in cleaned_data:
                del cleaned_data['user_resource_uri']

        return cleaned_data


class CourseDeleteUserForm(forms.Form):

    course_id = forms.CharField()
    user_resource_uri = forms.CharField()
    staff_or_instructor = forms.CharField()

    def clean_user_resource_uri(self):

        try:
            username = self.cleaned_data['user_resource_uri'].split('/')[-2:-1][0]
        except:
            username = None

        self._user = None
        if username:
            try:
                self._user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass

        if not self._user:
            raise forms.ValidationError('User object not found!')

        return self.cleaned_data

    def clean(self):
        cleaned_data = super(CourseDeleteUserForm, self).clean()

        try:
            group = Group.objects.get(name='%s_%s' % (
                cleaned_data.get('staff_or_instructor'), 
                cleaned_data.get('course_id')))
        except Group.DoesNotExist:
            group = None

        if group is None:
            msg = '%s group for %s does not exist! Please ' \
                'contact the server admin!' % (
                cleaned_data.get('staff_or_instructor').capitalize(), 
                cleaned_data.get('course_id'))
            self._errors['user_resource_uri'] = self.error_class([msg])
            if 'user_resource_uri' in cleaned_data:
                del cleaned_data['user_resource_uri']
        elif self._user not in group.user_set.all():
            msg = "User object is not a/an '%s'." % cleaned_data.get(
                'staff_or_instructor')
            self._errors['user_resource_uri'] = self.error_class([msg])
            if 'user_resource_uri' in cleaned_data:
                del cleaned_data['user_resource_uri']

        return cleaned_data


# USER


class UserCreateForm(forms.Form):

    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    username = forms.CharField(required=True)

    def clean(self):

        cleaned_data = super(UserCreateForm, self).clean()
        
        try:
            user = User.objects.get(
                Q(username=self.cleaned_data['username']) |
                Q(email=self.cleaned_data['email']))
        except User.DoesNotExist:
            user = None

        if user:
            if user.email == self.cleaned_data['email']:
                msg = 'Email already exists!'
                self._errors['email'] = self.error_class([msg])
                del cleaned_data['email']

            if user.username == self.cleaned_data['username']:
                msg = 'Username already exists!'
                self._errors['username'] = self.error_class([msg])
                del cleaned_data['username']

        return cleaned_data


class UserUpdateForm(forms.Form):

    name = forms.CharField(required=True)


class UserDeleteForm(forms.Form):

    confirm = forms.BooleanField(required=False)

    def clean_confirm(self):
        if not self.cleaned_data['confirm']:
            raise forms.ValidationError('This field must be true!')
        return self.cleaned_data['confirm']


class UserEnrollForm(forms.Form):

    username = forms.CharField()
    course_resource_uri = forms.CharField(required=True)

    def clean(self):
        " Validando se o usuário está matriculado no curso. "

        cleaned_data = super(UserEnrollForm, self).clean()

        try:
            course_id = course_id_decoder(cleaned_data.get(
                'course_resource_uri').split('/')[5])
        except:
            course_id = None

        if course_id is None or not has_course(course_id):
            msg = 'Course does not exist!'
            self._errors['course_resource_uri'] = self.error_class([msg])
            del cleaned_data['course_resource_uri']

        if is_user_enrolled(username=cleaned_data.get('username'), 
            course_id=course_id):
            msg = 'User is already enrolled!'.decode('utf-8')
            self._errors['course_resource_uri'] = self.error_class([msg])
            del cleaned_data['course_resource_uri']
        
        return cleaned_data


class UserUnenrollForm(forms.Form):

    username = forms.CharField()
    course_resource_uri = forms.CharField(required=True)

    def clean(self):
        " Validando se o usuário está matriculado no curso. "
        
        cleaned_data = super(UserUnenrollForm, self).clean()  

        try:
            course_id = course_id_decoder(cleaned_data.get(
                'course_resource_uri').split('/')[5])
        except:
            course_id = None        

        if course_id is None or not is_user_enrolled(
            username=cleaned_data.get('username'), course_id=course_id):
            msg = 'User is not enrolled or course does not exist!'
            self._errors['course_resource_uri'] = self.error_class([msg])
            del cleaned_data['course_resource_uri']
        
        return cleaned_data
