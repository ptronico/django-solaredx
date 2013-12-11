# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class SolarEDXBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return None