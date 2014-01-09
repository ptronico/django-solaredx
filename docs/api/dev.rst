.. _resources:

dev
===

Essa documentação cobre a versão ``dev`` da API. Todas as chamadas dessa 
versão contém, ``/api/dev/`` na URI.

.. .. contents::
..    :depth: 4

.. note::

    Use a extensão `Postman <https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en>`_ do Chrome ou o software 
    `Curl <http://curl.haxx.se/>`_ para "brincar" com a API enquanto você lê 
    essa documentação.

.. note::

    Embora faça parte do pacote SolarEDX, o sistema de login via Solar não 
    está implementado nessa API. Para maiores informações consulte o tópico
    :ref:`login`.

Notas Preliminares
------------------

Todas as requisições de consulta deverão ser feitas com HTTP GET.

Todas as requisições de escrita deverão ser feitas com HTTP POST.

Etc.

Sistema de Autenticação
-----------------------

TODO!

Gestão de Usuários
------------------

.. Essa sessão apresenta como gerenciar usuários.

Listagem e consulta de usuários
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para efetuar uma listagem geral de usuários do EDX, faça a consulta abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/

O resultado retornado segue abaixo, em JSON:

.. code-block:: json

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 2
        },
        "objects": [
            {
                "date_joined": "Wed, 2 Oct 2013 13:53:50 -0300",
                "email": "ptronico@gmail.com",
                "is_active": true,
                "name": null,
                "resource_uri": "/solaredx/api/dev/user/ptronico/",
                "username": "ptronico"
            },
            {
                "date_joined": "Wed, 2 Oct 2013 13:56:31 -0300",
                "email": "pedro@pedrorafa.com",
                "is_active": true,
                "name": null,
                "resource_uri": "/solaredx/api/dev/user/pedrorafa/",
                "username": "pedrorafa"
            }
        ]
    }

Filtrando usuários
""""""""""""""""""

Você pode adicionar alguns filtros a sua consulta. É possível filtrar os campos 
``date_joined``, ``username`` e ``email``. Para isso, você deverá usar a mesma 
sistemática de `field lookups <https://docs.djangoproject.com/en/1.4/ref/models/querysets/#field-lookups>`_
adotada pela ORM do Django. Por exemplo, para listar usuários cujo email seja
do Gmail, faça uma requisição como a que se segue:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/?email__icontains=@gmail.com

Para filtrar usuários cujo cadastro ocorreu a partir de uma determinada
data, faça uma requisição semelhante a que segue abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/?date_joined__gte=2013-10-02 13:55:00-03:00

Note que para o campo ``date_joined`` só será aceito uma data no formato 
``YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]``. Ex: ``2013-10-02 13:55:00-03:00``,
onde ``-03:00`` é o fuso-horário.


Consultando um usuário
""""""""""""""""""""""

Para consultar um usuário, basta acessar a URI contida no campo 
``resource_uri`` desse usuário. Por exemplo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/ptronico/

Essa requisição retorna o seguinte JSON:

.. code-block:: json

    {
        "course_resource_uri": "/solaredx/api/dev/user/ptronico/course/",
        "date_joined": "Wed, 2 Oct 2013 13:53:50 -0300",
        "email": "ptronico@gmail.com",
        "name": "Pedro Vasconcelos",
        "username": "ptronico"
    }

.. ----

.. Os `endpoints` da API relacionados aos usuários encontram-se 
.. em ``/api/dev/user/``. Veja abaixo como efetuar operações com usuários:

.. .. note::

..     Acessando ``/api/dev/user/schema/`` você terá a especificação técnica do
..     `endpoint` de usuários. Nem todas as informações contidas nesse esquema 
..     estão corretas. O ideal é se orientar por essa documentação.

.. Para listar usuários acesse a URI ``/solaredx/api/dev/user/``.

.. :Método:
..     ``GET``

.. :URI:
..     ``/solaredx/api/dev/user/``


Criação, modificação e exclusão de usuários
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As operações de criação, modificação e exclusão de usuários ocorrem mediante
uma requisição ``HTTP`` ``POST`` para a URI de consulta de usuários, isto é,
``/api/dev/user/``, enviando os campos ``username`` e ``action``. Outros campos
deverão também ser enviados, dependendo da operação desejada.

Criando um usuário
""""""""""""""""""

Para criação de um usuário, deverão ser enviados os campos ``username``, 
``name``, ``email`` e ``action`` (com o valor "create"). Veja o exemplo 
abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/ --data "username=nungo&name=Contato Nungo&email=contato@nungo.com.br&action=create"

Caso a operação seja efetuada com sucesso, será retornado o usuário criado. 
Veja a resposta da requisição acima:

.. code-block:: json

    {
        "course_resource_uri": "/solaredx/api/dev/user/nungo/course/",
        "date_joined": "Tue, 26 Nov 2013 11:46:11 -0300",
        "email": "contato@nungo.com.br",
        "name": "Contato Nungo",
        "username": "nungo"
    }

Durante a criação de usuário há a validação dos dados da requisição. Vamos 
tentar criar um usuário já existente. Observe a requisição abaixo: 

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/ --data "username=ptronico&name=Pedro&email=ptronico@gmail.com&action=create"

O JSON retornado segue abaixo:

.. code-block:: json

    {
        "errors": {
            "username": [
                "Username already exists!"
            ]
        },
        "status": "error"
    }

Sempre que houver algum erro haverá, no JSON retornado, o campo ``status`` 
com o valor ``error``. Além dele, haverá também a especificação do erro, 
conforme a requisição.

Modificando um usuário
""""""""""""""""""""""

Para modificar um usuário, faça uma requisição semelhante à requisição de 
criar usuário, com o valor do campo ``action`` igual a "update". 
Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/ --data "username=nungo&name=Nungo Tecnologia&email=contato@nungo.com.br&action=update"

Oberve a resposta:

.. code-block:: json

    {
        "course_resource_uri": "/solaredx/api/dev/user/nungo/course/",
        "date_joined": "Tue, 26 Nov 2013 11:46:11 -0300",
        "email": "contato@nungo.com.br",
        "name": "Nungo Tecnologia",
        "username": "nungo"
    }

Excluíndo um usuário
""""""""""""""""""""

Para excluir um usuário, deve-se fazer uma requisição enviando os campos 
``username`` e ``action`` (com o valor "delete"). Veja o exemplo: 

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/dev/user/ --data "username=nungo&action=delete"

Essa requisição retorna o JSON abaixo:

.. code-block:: json

    { 
        "status": "success" 
    }

.. Alocação e desalocação de usuários em cursos (matrícula)
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Alocando um usuário em um curso
.. """""""""""""""""""""""""""""""

.. bbb

.. Desalocando um usuário em um curso
.. """"""""""""""""""""""""""""""""""

.. ccc

.. **Alocação de usuários (alunos) em cursos**

.. Para alocar usuários (alunos) em cursos, deve-se fazer uma requisição de 
.. acordo com as informações abaixo. Note (veja a URI) que esse é um `endpoint` 
.. interno ao do usuário.

.. :Método:
..     ``POST``

.. :URI:
..     ``/solaredx/api/dev/user/<username>/course/``

.. :Parâmetros:

..     ``course_id``
..         Id do curso. Ex: ``UFC/CT101/2014.01``.

..     ``enrollment_action``
..         Ação a ser realizada. As opções válidas são ``enroll`` e ``unenroll``.


.. Gestão de Cursos
.. ----------------

.. Criação e exclusão de cursos
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Consulta e listagem de cursos
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Alocação e desalocação de professores e tutores em cursos
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Para listar cursos acesse a URI ``/solaredx/api/dev/course/``.

.. :Método:
..     ``GET``

.. :URI:
..     ``/solaredx/api/dev/course/``