# -*- coding: utf-8 -*-

# Python
import json

# Django
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

# SolarEDX
from .edx import course_delete

"""
Não utilizamos o ``tastypie.test.ResourceTestCase`` pois há um bug devido à
incompatibilidade entre a versão do Tastypie (0.9.16) com a do Django (1.4.8).
"""


class UserResourceTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_user_endpoint(self):

        # ETAPA 1 - Consultando usuários
        # ------------------------------

        # Efetuando requisição
        response = self.client.get('/solaredx/api/v1/user/')
        
        # Parser da resposta
        response_data = json.loads(response.content)

        # Checando código de status da resposta
        self.assertEqual(response.status_code, 200)

        # Checando a lista de objetos retornado
        self.assertEqual(len(response_data['objects']), 0)        
        
        # ETAPA 2 - Criando usuário
        # -------------------------

        request_data = {
            'username': 'ptronico',
            'name': 'Pedro',
            'email': 'ptronico@gmail.com',
        }

        response = self.client.post('/solaredx/api/v1/user/', 
            content_type='application/json', data=json.dumps(request_data))

        self.assertEqual(response.status_code, 201)

        # ETAPA 3 - Verificando se o usuário foi criado
        # ---------------------------------------------

        response = self.client.get('/solaredx/api/v1/user/ptronico/')        
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], request_data['name'])
        self.assertEqual(response_data['email'], request_data['email'])
        self.assertEqual(response_data['username'], request_data['username'])

        # ETAPA 4 - Atualizando usuário
        # -----------------------------

        request_data = {
            'name': 'Pedro Vasconcelos',
        }

        response = self.client.post('/solaredx/api/v1/user/ptronico/', 
            content_type='application/json', data=json.dumps(request_data), 
            HTTP_X_HTTP_METHOD_OVERRIDE='PATCH')

        self.assertEqual(response.status_code, 202)

        # ETAPA 5 - Checando se usuário foi atualizado
        # --------------------------------------------

        response = self.client.get('/solaredx/api/v1/user/ptronico/')
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['name'], request_data['name'])


class CourseResourceTest(TestCase):       

    fixtures = ['auth__group.json', 
        'auth__user.json', 'student__user_profile.json']

    def setUp(self):
        self.client = Client()
        
        try:
            # Deletando curso
            course_delete('UFC/CT001/2014.1')
        except:
            pass

    def test_course_endpoint(self):

        # ETAPA 1 - Consultando cursos
        # ----------------------------

        response = self.client.get('/solaredx/api/v1/course/')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['objects']), 0)

        # ETAPA 2 - Criando um curso
        # --------------------------

        request_data = {
            'course_id': 'UFC/CT001/2014.1',
            'display_name': 'Curso Teste',
            'course_creator_username': 'ptronico',
        }

        response = self.client.post('/solaredx/api/v1/course/',
            content_type='application/json', data=json.dumps(request_data))

        self.assertEqual(response.status_code, 201)
        
        # ETAPA 3 - Verificando se o curso foi criado
        # -------------------------------------------

        response = self.client.get('/solaredx/api/v1/course/')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['objects']), 1)

        course_resource_uri = response_data['objects'][0]['resource_uri']
        response = self.client.get(course_resource_uri)
        response_data = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['course_id'], request_data['course_id'])
        self.assertEqual(response_data['display_name'], 
            request_data['display_name'])

        # ETAPA 4 - Atualizando um curso
        # ------------------------------


        # ETAPA 5 - Deletando um curso
        # ----------------------------

        request_data = {
            'confirm': True,
        }

        response = self.client.post(course_resource_uri, 
            content_type='application/json', data=json.dumps(request_data),
            HTTP_X_HTTP_METHOD_OVERRIDE='DELETE')

        self.assertEqual(response.status_code, 204)

        # ETAPA 6 - Confirmando se o curso foi deletado
        # ---------------------------------------------

        response = self.client.get('/solaredx/api/v1/course/')
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_data['objects']), 0)





        
