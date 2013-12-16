# -*- coding: utf-8 -*-

from django import forms

from xmodule.modulestore.exceptions import ItemNotFoundError

from student.views import course_from_id
from student.models import CourseEnrollment


class CourseEnrollmentUpdateForm(forms.Form):

    course_id = forms.CharField()
    enrollment_action = forms.CharField()

    def clean_course_id(self):

        try:
            course = course_from_id(self.cleaned_data['course_id'])
        except ItemNotFoundError:
            raise forms.ValidationError('Invalid course id!')

        return self.cleaned_data['course_id']

    def clean_enrollment_action(self):

        actions = ['enroll', 'unenroll']

        if self.cleaned_data['enrollment_action'] not in actions:
            raise forms.ValidationError('Invalid enrollment action!')

        return self.cleaned_data['enrollment_action']

    def update_enrollment(self, user):
        " Perform a course enrollment update. "

        if self.cleaned_data['enrollment_action'] == 'enroll':
            CourseEnrollment.enroll(user, self.cleaned_data['course_id'])

        if self.cleaned_data['enrollment_action'] == 'unenroll':
            CourseEnrollment.unenroll(user, self.cleaned_data['course_id'])

