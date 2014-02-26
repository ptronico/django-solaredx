# -*- coding: utf-8 -*-

# Django
from django.contrib.auth.models import User, Group

# EDX
from student.models import UserProfile, CourseEnrollment
from auth.authz import create_all_course_groups
from contentstore.utils import delete_course_and_groups
from contentstore.views.tabs import initialize_course_tabs
from django_comment_common.utils import seed_permissions_roles
from xmodule.course_module import CourseDescriptor
from xmodule.html_module import AboutDescriptor
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore.exceptions import (ItemNotFoundError, 
    InvalidLocationError, InsufficientSpecificationError)

# SolarEDX
from .utils import generate_random_hexcode


# USER - Funções relacionadas a cursos
# ------------------------------------


# Validação

def is_user_enrolled(username, course_id):
    try:
        user = User.objects.get(username=username)
        is_enrolled = CourseEnrollment.is_enrolled(user, course_id)
    except:
        is_enrolled = False
    return is_enrolled


# CRUD

def user_create(data):
    """
    Cria um usuário no EDX.
    """

    # Criando usuário (cria já ativado)
    user = User.objects.create_user(username=data['username'], 
        email=data['email'], password=generate_random_hexcode(30))

    # Ativando usuário
    user.is_active = True
    user.save()
    
    # Criando o perfil do usuário    
    profile = UserProfile.objects.create(user=user, name=data['name'])

def user_update(username, data):
    """
    Atualiza o usuário no EDX.
    """

    # Recuperando usuário
    user = User.objects.select_related('profile').get(username=username)
    profile = user.get_profile()

    # Atualizando profile
    if 'name' in data:
        profile.name = data['name']
        profile.save()

def user_delete(username):
    """
    Deleta o usuário no EDX.

    Atenção: essa função não deve ser utilizada, pois o EDX não deleta usuários.
    """

    # Recuperando usuário
    user = User.objects.get(username=username)

    # Deletando usuário
    # user.delete()

# Matrícula

def user_enroll(username, course_id):
    " Matricula um usuário em um curso. "
    user = User.objects.get(username=username)
    CourseEnrollment.enroll(user, course_id)

def user_unenroll(username, course_id):
    " Desmatricula um usuário em um curso. "
    user = User.objects.get(username=username)
    CourseEnrollment.unenroll(user, course_id)

# Outros

def get_course_id_list_as_staff_or_instructor(username, staff_or_instructor):
    " Retorna os IDs dos cursos em que o usuário é instructor/staff. "

    course_id_set = set()
    group_name_prefix = '%s_' % staff_or_instructor
    user = User.objects.get(username=username)    

    for group in user.groups.filter(name__startswith=group_name_prefix):
        course_id_set.add(group.name.replace(group_name_prefix, ''))

    return list(course_id_set)

# COURSE - Classes e funções relacionadas a cursos
# ------------------------------------------------


def has_course(course_id):
    try:
        course_loc = CourseDescriptor.id_to_location(course_id)
        course = modulestore().get_instance(course_id, course_loc)
        result = True
    except:
        result = False
    return result

class CourseValidator(object):
    """
    Essa classe auxilia a validação dos dados recebidos na gestão de cursos.
    """

    def __init__(self, course_id=None, 
        display_name=None, course_creator_username=None):

        self.display_name = display_name

        try:
            self.org, self.number, self.run = course_id.split('/')
        except:
            self.org, self.number, self.run = None, None, None

        if course_creator_username:
            try:
                self.course_creator = User.objects.get(
                    username=course_creator_username)
            except User.DoesNotExist:
                self.course_creator = None
        else:
            self.course_creator = None

    def is_course_id_valid(self):
        " Retorna verdadeiro se o nome do curso é válido. "
        
        if self.org is None or self.number is None or self.run is None:
            return False            

        try:
            Location('i4x', self.org, self.number, 'course', self.run)
        except InvalidLocationError as error:
            return False

        return True

    def does_course_exist(self):
        " Retorna verdadeiro se o curso já existe. "
        try:
            modulestore('direct').get_item(
                Location('i4x', self.org, self.number, 'course', self.run))
            return True
        except (ItemNotFoundError, InsufficientSpecificationError):
            return False

    def does_course_creator_exist(self):
        " Retorna verdadeiro se o usuário criador do curso existe. "
        return True if self.course_creator else False

# Operações

def course_create(data):
    """
    Cria um curso no EDX.

    Essa função é baseada na função localizada em
    ``cms.contentstore.views.course.create_new_course``.

    """

    # ETAPA 1 - Preparando dados
    # --------------------------

    org, number, run = data['course_id'].split('/')

    course_creator = User.objects.get(username=data['course_creator_username'])

    # ETAPA 2 - Criando curso
    # -----------------------

    course_metadata = { 
        'display_name': data['display_name'],
    }

    dest_location = Location('i4x', org, number, 'course', run)

    modulestore('direct').create_and_save_xmodule(
        dest_location, metadata=course_metadata)

    new_course = modulestore('direct').get_item(dest_location)

    dest_about_location = dest_location.replace(
        category='about', name='overview')
    
    overview_template = AboutDescriptor.get_template('overview.yaml')
    
    modulestore('direct').create_and_save_xmodule(
        dest_about_location, system=new_course.system, 
        definition_data=overview_template.get('data'))

    initialize_course_tabs(new_course)
    create_all_course_groups(course_creator, new_course.location)
    seed_permissions_roles(new_course.location.course_id)

    CourseEnrollment.enroll(course_creator, new_course.location.course_id)

    new_location = loc_mapper().translate_location(
        new_course.location.course_id, new_course.location, False, True)

    return new_course

def course_update(course_id, data):
    """
    Atualiza um curso.

    Essa função não executa nenhuma ação. Qualquer modificação no curso deve
    ser feito no próprio EDX.
    """

    # from models.settings.course_details import CourseDetails

    # org, number, run = data['course_id'].split('/')

    # # Formato data: '2014-03-10T23:00:00.000Z'

    # update_data = {
    #     'course_location': ['ix4', org, number, 'course', run, null],
    #     'start_date': data['start'],
    #     'end_date': data['end'],
    #     'enrollment_start': data['enrollment_start'],
    #     'enrollment_end': data['enrollment_end'],
    # }

    # CourseDetails.update_from_json(update_data)

    return

def course_delete(course_id):
    """
    Deleta um curso no EDX.
    """
    delete_course_and_groups(course_id, True)

def course_add_user(course_id, username, staff_or_instructor):
    user = User.objects.get(username=username)
    group = Group.objects.get(name='%s_%s' % (staff_or_instructor, course_id))
    group.user_set.add(user)

def course_remove_user(course_id, username, staff_or_instructor):
    user = User.objects.get(username=username)
    group = Group.objects.get(name='%s_%s' % (staff_or_instructor, course_id))
    group.user_set.remove(user)


