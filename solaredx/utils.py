# -*- coding: utf-8 -*-

import hmac
import random
import base64
import hashlib

from django.conf import settings

from xmodule.modulestore.django import loc_mapper

class Course(object):
    """
    Course object, a mix of RDBMS fields (course_id) with NoSQL fields (name).
    """

    pk = 1
    staff = 1
    course_id = ''
    course_absolute_url = ''
    course_absolute_url_lms = ''
    course_absolute_url_studio = ''
    display_name = ''
    start = ''
    end = ''
    enrollment_start = ''
    enrollment_end = ''

    @property
    def course_id_solaredx(self):
        return course_id_encoder(self.course_id)


def mount_course_object_list(course_object_list):
    """
    A custom helper method for reusable mounting object list.
    """

    object_list = []

    for course in course_object_list:

        course_loc = loc_mapper().translate_location(
            course.location.course_id, course.location, 
            published=False, add_entry_if_missing=True)

        c = Course()

        c.course_id = course.id
        c.display_name = course.display_name

        # URLs
        c.course_absolute_url = build_lms_absolute_url(
            '/courses/%s/about' % course.id)

        c.course_absolute_url_lms = build_lms_absolute_url(
            '/courses/%s/info' % course.id)

        c.course_absolute_url_studio = build_cms_absolute_url(
            course_loc.url_reverse('course/', ''))            

        c.start = course.start
        c.end = course.end
        c.enrollment_start = course.enrollment_start
        c.enrollment_end = course.enrollment_end

        object_list.append(c) 

    return object_list

def course_id_encoder(value):
    return base64.b16encode(value).lower()

def course_id_decoder(value):
    return base64.b16decode(value.upper())

def solaredx_encrypt(value):
    return hmac.new(settings.SOLAREDX_SECRET_KEY, 
        value, hashlib.sha1).hexdigest()

def generate_random_hexcode(length):
    return ('%x' % random.randrange(16**length)).zfill(length)

def build_lms_absolute_url(path):
    # return 'http://localhost:8000%s' % path
    return 'http://solaredx.virtual.ufc.br%s' % path

def build_cms_absolute_url(path):
    # return 'http://localhost:8001%s' % path
    return 'http://solaredxstd.virtual.ufc.br%s' % path