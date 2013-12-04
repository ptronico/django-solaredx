# -*- coding: utf-8 -*-

import base64

def course_id_encoder(value):
    return base64.b16encode(value).lower()