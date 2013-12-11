# -*- coding: utf-8 -*-

from django import forms


class CourseEnrollmentUpdate(forms.Form):

    course_id = forms.CharField()
    username = forms.CharField()
    is_active = forms.BooleanField()