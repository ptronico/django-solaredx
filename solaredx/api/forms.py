# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User, Group

from xmodule.modulestore.exceptions import ItemNotFoundError

from student.views import course_from_id
from student.models import CourseEnrollment


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
