# -*- coding: utf-8 -*-

import re
import bson

# Django
from django import forms
from django.contrib.auth.models import User, Group

# EDX
from auth.authz import create_all_course_groups
from contentstore.utils import delete_course_and_groups
from contentstore.views.tabs import initialize_course_tabs
from django_comment_common.utils import seed_permissions_roles
from student.views import course_from_id
from student.models import UserProfile, CourseEnrollment
from xmodule.html_module import AboutDescriptor
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore.exceptions import (ItemNotFoundError, 
    InvalidLocationError, InsufficientSpecificationError)

# SolarEDX
from .resources.utils import course_exists
from ..utils import generate_random_hexcode


class ManageCourseForm(forms.Form):

    course_id = forms.CharField()
    display_name = forms.CharField(required=False)
    course_creator_username = forms.CharField(required=False)
    action = forms.CharField()

    def __init__(self, *args, **kwargs):
        self._org, self._number, self._run, self._creator = \
            None, None, None, None
        super(ManageCourseForm, self).__init__(*args, **kwargs)

    def clean_course_id(self):
        try:
            self._org, self._number, self._run = \
                self.cleaned_data['course_id'].split('/')
        except:
            pass
        
        if not self._org or not self._number or not self._run:
            raise forms.ValidationError('Invalid course_id!')

        # Validando Course Location
        try:
            self._dest_location = Location('i4x', self._org, self._number, 
                'course', self._run)
        except InvalidLocationError as error:
            # self._dest_location = None
            # self._errors['course_id'] = self.error_class([error.message])
            # if 'course_id' in cleaned_data: del cleaned_data['course_id']
            raise forms.ValidationError('Invalid course_id!')

        return self.cleaned_data['course_id']

    def clean_action(self):
        valid_actions = ['create', 'delete']
        if self.cleaned_data['action'] not in valid_actions:
            raise forms.ValidationError('Invalid action!')
        return self.cleaned_data['action']

    def clean(self):

        cleaned_data = super(ManageCourseForm, self).clean()

        # Validando a requisição de criação de curso
        if 'create' in cleaned_data.get('action', ''):

            # Validando 'display_name'
            if not cleaned_data.get('display_name', ''):
                self._errors['display_name'] = self.error_class(
                    ['This field is required.'])
                if 'display_name' in cleaned_data: 
                    del cleaned_data['display_name']

            # Validando 'course_creator_username'
            if not cleaned_data.get('course_creator_username', ''):
                self._errors['course_creator_username'] = self.error_class(
                    ['This field is required.'])
                if 'course_creator_username' in cleaned_data: 
                    del cleaned_data['course_creator_username']
            else:
                try:
                    self._creator = User.objects.get(
                        username=cleaned_data.get('course_creator_username', ''))
                except User.DoesNotExist:
                    self._errors['course_creator_username'] = self.error_class(
                        ['Invalid username!'])
                    if 'course_creator_username' in cleaned_data: 
                        del cleaned_data['course_creator_username']

            # Validando a inexistência do curso
            if self._dest_location and course_exists(self._dest_location):            
                self._errors['course_id'] = self.error_class(
                    ['Course already exists!'])
                if 'course_id' in cleaned_data: 
                    del cleaned_data['course_id']

        # Validando a requisição de deleção do curso
        if 'delete' in cleaned_data.get('action', '') and self._dest_location \
            and not course_exists(self._dest_location):
            self._errors['course_id'] = self.error_class(
                ['Course does not exists!'])
            if 'course_id' in cleaned_data: 
                del cleaned_data['course_id']

        return cleaned_data

    def update(self):

        course = None

        if self.cleaned_data['action'] == 'create':
            # Criando um curso, conforme 
            # 'cms.contentstore.views.course.create_new_course'

            course_metadata = { 
                'display_name': self.cleaned_data['display_name'],
            }

            # Criando o curso
            modulestore('direct').create_and_save_xmodule(self._dest_location,
                metadata=course_metadata)

            new_course = modulestore('direct').get_item(self._dest_location)

            # clone a default 'about' overview module as well
            dest_about_location = self._dest_location.replace(
                category='about', name='overview')
            
            overview_template = AboutDescriptor.get_template('overview.yaml')
            
            modulestore('direct').create_and_save_xmodule(
                dest_about_location, system=new_course.system, 
                definition_data=overview_template.get('data'))

            initialize_course_tabs(new_course)
            create_all_course_groups(self._creator, new_course.location)
            seed_permissions_roles(new_course.location.course_id)

            # Auto-enroll the course creator. So that "View Live" will work.
            CourseEnrollment.enroll(self._creator, 
                new_course.location.course_id)

            new_location = loc_mapper().translate_location(
                new_course.location.course_id, new_course.location, False, True)

            course = new_course

        if self.cleaned_data['action'] == 'delete':
            # Excluindo um curso
            delete_course_and_groups(self.cleaned_data['course_id'], True)

        return course


class ManageUserForm(forms.Form):

    name = forms.CharField(required=True)
    email = forms.CharField()
    username = forms.CharField()
    action = forms.CharField()

    def __init__(self, *args, **kwargs):
        self._user = None
        super(ManageUserForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        return self.cleaned_data['name']

    def clean_email(self):
        return self.cleaned_data['email']

    def clean_username(self):
        try:
            self._user = User.objects.get(
                username=self.cleaned_data['username'])
        except User.DoesNotExist:
            self._user = None
        return self.cleaned_data['username']

    def clean_action(self):
        valid_actions = ['create', 'update', 'delete']
        if self.cleaned_data['action'] not in valid_actions:
            raise forms.ValidationError('Invalid action!')
        return self.cleaned_data['action']

    def clean(self):

        cleaned_data = super(ManageUserForm, self).clean()

        if 'create' in cleaned_data.get('action', '') and self._user:
            # Erro se tentando criar usuário com username já existente
            self._errors['username'] = self.error_class(
                ['Username already exists!'.decode('utf-8')])
            if 'username' in cleaned_data: del cleaned_data['username']

        if ('update' in cleaned_data.get('action', '') or \
            'delete' in cleaned_data.get('action', '')) and not self._user:
            # Erro se tentando atualizar ou deletar usuário não existente
            self._errors['username'] = self.error_class(
                ['User does not exists!'.decode('utf-8')])
            if 'username' in cleaned_data: del cleaned_data['username']

        return cleaned_data

    def update(self):

        if self.cleaned_data['action'] == 'create':
            # Criando usuário
            self._user = User()
            self._user.username = self.cleaned_data['username']
            self._user.email = self.cleaned_data['email']
            self._user.is_active = True
            self._user.set_password(generate_random_hexcode(30))
            self._user.save()

            profile = UserProfile()
            profile.user = self._user
            profile.name = self.cleaned_data['name']
            profile.save()

        if self.cleaned_data['action'] == 'update':
            # Atualizando
            self._user.email = self.cleaned_data['email']
            self._user.is_active = True
            self._user.save()

            profile = self._user.profile
            profile.name = self.cleaned_data['name']
            profile.save()

        if self.cleaned_data['action'] == 'delete':
            # Deletando usuário
            # TODO: garantir que a deleção remova todos os dados relacionados
            # ao usuário.
            self._user.delete()

        return self._user


class ManageCourseUserForm(forms.Form):

    username = forms.CharField()
    action = forms.CharField()

    def clean_username(self):
        try:
            self._user = User.objects.get(
                username=self.cleaned_data['username'])
        except User.DoesNotExist:
            self._user = None

        if self._user is None:
            raise forms.ValidationError('Invalid username!')

        return self.cleaned_data['username']

    def clean_action(self):

        actions = ['add', 'remove']

        if self.cleaned_data['action'] not in actions:
            raise forms.ValidationError('Invalid action!')

        return self.cleaned_data['action']

    def update(self, course_id, staff_or_instructor):

        try:
            group = Group.objects.get(
                name='%s_%s' % (staff_or_instructor, course_id))
        except Group.DoesNotExist:
            group = None

        if 'add' in self.cleaned_data['action']:
            group.user_set.add(self._user)
        else:
            group.user_set.remove(self._user)

        return self.cleaned_data['action'], self._user


class CourseEnrollmentUpdateForm(forms.Form):

    course_id = forms.CharField()
    action = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(CourseEnrollmentUpdateForm, self).__init__(*args, **kwargs)
        self._course = None

    def clean_course_id(self):

        try:
            self._course = course_from_id(self.cleaned_data['course_id'])
        except ItemNotFoundError:
            raise forms.ValidationError('Invalid course id!')

        return self.cleaned_data['course_id']

    def clean_action(self):

        actions = ['add', 'remove']

        if self.cleaned_data['action'] not in actions:
            raise forms.ValidationError('Invalid action!')

        return self.cleaned_data['action']

    def update_enrollment(self, user):
        " Perform a course enrollment update. "

        if self.cleaned_data['action'] == 'add':
            CourseEnrollment.enroll(user, self.cleaned_data['course_id'])

        if self.cleaned_data['action'] == 'remove':
            CourseEnrollment.unenroll(user, self.cleaned_data['course_id'])

        return self._course
