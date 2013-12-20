.. _resources:

API
===

A API do SolarEDX utiliza a biblioteca 
`Tastypie <django-tastypie.readthedocs.org>`_. As funcionalidades implementadas
até o momento são:


- Gestão de Cursos
 - Listagem de Cursos
 - Gestão de usuários "instructor" e "staff" em cursos
- Gestão de Usuários
 - Listagem de Usuários
 - Filtragem de Usuários
 - Matrícula de usuários em cursos




Gestão de Cursos
------------------

Para listar cursos acesse a URI ``/solaredx/api/dev/course/``.

:Método:
    ``GET``

:URI:
    ``/solaredx/api/dev/course/``



Gestão de Usuários
--------------------

Para listar usuários acesse a URI ``/solaredx/api/dev/user/``.

:Método:
    ``GET``

:URI:
    ``/solaredx/api/dev/user/``


**Alocação de usuários (alunos) em cursos**

Para alocar usuários (alunos) em cursos, deve-se fazer uma requisição de 
acordo com as informações abaixo. Note (veja a URI) que esse é um `endpoint` 
interno ao do usuário.

:Método:
    ``POST``

:URI:
    ``/solaredx/api/dev/user/<username>/course/``

:Parâmetros:

    ``course_id``
        Id do curso. Ex: ``UFC/CT101/2014.01``.

    ``enrollment_action``
        Ação a ser realizada. As opções válidas são ``enroll`` e ``unenroll``.