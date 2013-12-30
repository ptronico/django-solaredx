# -*- coding: utf-8 -*-

import hmac
import random
import base64
import hashlib

from django.conf import settings

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