.. _resources:

API-v1
======

.. Antes de ler esse artigo é recomendada a leitura do artigo :ref:`Quickstart <quickstart>`.

Essa documentação cobre a versão ``v1`` da API. Todas as chamadas dessa 
versão contém, ``/api/v1/`` na URI.

.. .. contents::
..    :depth: 4

.. note::

    Uma regra geral é que todas as requisições de consulta/leitura deverão 
    ser realizadas com ``HTTP`` ``GET``, e as requisições de 
    modificação/escrita com ``HTTP`` ``POST``, ``PATCH`` ou ``DELETE`` para
    criação, modificação ou exclusão, respecitvamente. Todas as requisições
    retornam o ``status_code`` mais adequado o possível. Para mais informações
    consulte o artigo `Status Code Definitions <http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html>`_.

.. note::

    Utilize o `Curl <http://curl.haxx.se/>`_ ou a extensão `Postman 
    <https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en>`_ 
    do Chrome para "brincar" com a API enquanto você lê essa documentação.

.. note::

    Embora faça parte do pacote SolarEDX, o sistema de login via Solar não 
    está implementado nessa API. O motivo principal é que a arquitetura do 
    :ref:`Sistema de Login Simplificado <login>` quebra os princípios 
    utilizados na API.


Introdução
----------

A API provida pelo SolarEDX permite as seguintes chamadas:

Chamadas relacionadas à usuários:

* Criar usuários;
* Listar usuários;
* Consultar um usuário;
* Atualizar um usuário;
* Listar cursos em que o usuário está matriculado;
* Matricular e desmatricular usuários;

Chamadas relacionadas à cursos:

* Criar cursos;
* Listar cursos;
* Consultar um curso;
* Deletar um curso;
* Listar professores e tutures de um curso;
* Associar professores e tutores à um curso;
* Desassociar professores e tutores à um curso;

Sistema de Segurança / Autenticação
-----------------------------------

Uma vez que a API provida pelo SolarEDX permite ações globais de controle e, 
em decorrência disso, o acesso será restrito à apenas clientes autorizados e 
com IP fixo (por exemplo, o servidor do Solar). Nesse caso, a restrição de 
acesso deverá ser configurada no servidor do EDX, de modo a bloquear qualquer 
requisição à API que venha de um IP não autorizado.

.. note::
    O módulo ``ngx_http_access_module`` permite a instalação desse sistema de 
    segurança com o `Nginx <http://nginx.org/en/docs/http/ngx_http_access_module.html>`_.

Gestão de Usuários
------------------

Essa sessão apresenta como gerenciar usuários.

Listagem e consulta de usuários
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para efetuar uma listagem geral de usuários do EDX, faça uma requisição GET,
como segue no exemplo abaixo. Observe que o primeiro bloco é um comando 
que utiliza o cURL para fazer a requisição, e o segundo bloco é o cabeçalho
da requisição realizada:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/

.. code-block:: text

    GET /solaredx/api/v1/user/ptronico/course/ HTTP/1.1
    Host: localhost:8001

Veja os dados retornados da requisição acima. O primeiro bloco consiste no
cabeçalho da resposta. O segundo, nos dados recebidos, em formato JSON:

.. code-block:: text

    HTTP/1.0 200 OK
    Server: WSGIServer/0.1 Python/2.7.1
    Content-Type: application/json

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
                "resource_uri": "/solaredx/api/v1/user/ptronico/",
                "username": "ptronico"
            },
            {
                "date_joined": "Wed, 2 Oct 2013 13:56:31 -0300",
                "email": "pedro@pedrorafa.com",
                "is_active": true,
                "name": null,
                "resource_uri": "/solaredx/api/v1/user/pedrorafa/",
                "username": "pedrorafa"
            }
        ]
    }    

.. note::
    Os cabeçalhos mostrados na nessa documentação, tanto da da requisição e 
    da resposta, tem o objetivo de mostrar as informações essenciais para a
    realização da requisição e correto recebimento da resposta, e portanto
    podem ter alguns de seus elementos suprimidos.

Filtrando usuários
""""""""""""""""""

Você pode adicionar alguns filtros a sua consulta. É possível filtrar os campos 
``date_joined``, ``username`` e ``email``. Para isso, você deverá usar a mesma 
sistemática de `field lookups <https://docs.djangoproject.com/en/1.4/ref/models/querysets/#field-lookups>`_
adotada pela ORM do Django. Por exemplo, para listar usuários cujo email seja
do Gmail, faça uma requisição como a que se segue:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/?email__icontains=@gmail.com

Para filtrar usuários cujo cadastro ocorreu a partir de uma determinada
data, faça uma requisição semelhante a que segue abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/?date_joined__gte=2013-10-02 13:55:00-03:00

Note que para o campo ``date_joined`` só será aceito uma data no formato 
``YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]``. Ex: ``2013-10-02 13:55:00-03:00``,
onde ``-03:00`` é o fuso-horário.


Consultando um usuário
""""""""""""""""""""""

Para consultar um usuário, basta acessar a URI contida no campo 
``resource_uri`` desse usuário. Por exemplo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ptronico/

.. code-block:: text

    GET /solaredx/api/v1/user/ptronico/ HTTP/1.1
    Host: localhost:8001

Essa requisição retorna o seguinte:

.. code-block:: text

    HTTP/1.0 200 OK
    Content-Type: application/json

.. code-block:: json

    {
        "course_resource_uri": "/solaredx/api/v1/user/ptronico/course/",
        "date_joined": "Wed, 2 Oct 2013 13:53:50 -0300",
        "email": "ptronico@gmail.com",
        "name": "Pedro Vasconcelos",
        "username": "ptronico"
    }

Se você consultar um usuário que não existe será retornado uma resposta
``404 NOT FOUND``. Veja a requição abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/fulano/

.. code-block:: text

    GET /solaredx/api/v1/user/fulano/ HTTP/1.1
    Host: localhost:8001

E a respectiva resposta (apenas cabeçalho, não retorna dados):

.. code-block:: text

    HTTP/1.0 404 NOT FOUND
    Content-Type: text/html; charset=utf-8

Criação, modificação e exclusão de usuários
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Criando um usuário
""""""""""""""""""

A operação de criação de usuários ocorre mediante uma requisição ``HTTP`` 
``POST`` para a URI de listagem de usuários, isto é, ``/api/v1/user/``, 
enviando os campos ``username``, ``email`` e ``name`` codificandos em JSON. 
Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ --header 'Content-Type: application/json' --data '{ "username": "ptronico", "name": "Pedro Vasconcelos", "email": "ptronico@gmail.com" }'

.. code-block:: text

    POST /solaredx/api/v1/user/ HTTP/1.1
    Host: localhost:8001
    Content-Type: application/json

Caso a operação seja efetuada com sucesso, será retornado uma resposta 
``201 CREATED``. Veja a resposta da requisição acima:

.. code-block:: text

    HTTP/1.0 201 CREATED
    Content-Type: application/json

.. code-block:: json

    {
        "email": "ptronico@gmail.com",
        "name": "Pedro Vasconcelos",
        "username": "ptronico"
    }

Durante todas as requisições de modificações ou deleções de dados, bem como
no caso da criação de usuário, há a validação dos dados da requisição. Para
efeito de demonstração, iremos tentar criar um usuário já existente. Para isso
iremos repetir a requisição anteior. Observe a requisição abaixo: 

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ --header 'Content-Type: application/json' --data '{ "username": "ptronico", "name": "Pedro Vasconcelos", "email": "ptronico@gmail.com" }'

.. code-block:: text

    POST /solaredx/api/v1/user/ HTTP/1.1
    Host: localhost:8001
    Content-Type: application/json

Observe que a resposta da requisição retornou a informação ``400 BAD REQUEST``.
O JSON retornado também segue abaixo:

.. code-block:: text

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json

.. code-block:: json

    {
        "email": [
            "Email already exists!"
        ],
        "username": [
            "Username already exists!"
        ]
    }

Observe que no JSON retornado há uma mensagem informando o motivo pelo qual a
requisição foi retornada como `Bad Request`.

.. note :: 

    Sempre que uma requisição não for realizada com sucesso, por exemplo, 
    por envio incorreto de dados, será retornado ``400 BAD REQUEST``. Isso vale
    para qualquer requisição incorreta.

Modificando um usuário
""""""""""""""""""""""

Para modificar um usuário, faça uma requisição semelhante à requisição de 
criar usuário, com o valor do campo ``action`` igual a "update". 
Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ptronico/ -X PATCH --header 'Content-Type: application/json' --data '{ "name": "Pedro Rafael A. C. Vasconcelos" }'

.. code-block:: text

    PATCH /solaredx/api/v1/user/ptronico/ HTTP/1.1
    Host: localhost:8001
    Content-Type: application/json

Observe a resposta:

.. code-block:: text

    HTTP/1.0 202 ACCEPTED
    Content-Type: application/json

.. code-block:: json

    {
        "name": "Pedro Rafael A. C. Vasconcelos"
    }

.. Excluíndo um usuário
.. """"""""""""""""""""

.. Para excluir um usuário, deve-se fazer uma requisição enviando os campos 
.. ``username`` e ``action`` (com o valor "delete"). Veja o exemplo: 

.. .. code-block:: bash

..     $ curl http://localhost:8001/solaredx/api/v1/user/ --data "username=nungo&action=delete"

.. Essa requisição retorna o JSON abaixo:

.. .. code-block:: json

..     { 
..         "status": "success" 
..     }

Alocação e desalocação de usuários em cursos (matrícula)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para consultar em quais cursos o usuário está matriculado, iremos acessar a 
URI contida no campo ``course_resource_uri`` do usuário. Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ptronico/course/

.. code-block:: text

    GET /solaredx/api/v1/user/ptronico/course/ HTTP/1.1
    Host: localhost:8001

Como resposta temos:

.. code-block:: text

    HTTP/1.0 200 OK
    Content-Type: application/json

.. code-block:: json

    [
        "/solaredx/api/v1/course/5546432f433030322f323031342e32/",
        "/solaredx/api/v1/course/5546432f43533130312f323031335f46616c6c/",
        "/solaredx/api/v1/course/5546432f43533130322f323031342e32/",
        "/solaredx/api/v1/course/5546432f43543130312f323031345f3031/"
    ]

Alocando um usuário em um curso
"""""""""""""""""""""""""""""""

Para alocar (matricular) um usuário em um curso, deve-se fazer uma requisição
``HTTP`` ``POST`` para a URI ``/api/v1/user/<username>/course/`` com os campos
``course_id`` e ``action`` (com o valor ``add``). Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ptronico/course/ -X POST --header 'Content-Type: application/json' --data '{ "course_resource_uri": "/solaredx/api/v1/course/5546432f43533130322f323031342e32/" }'

.. code-block:: text

    POST /solaredx/api/v1/user/ptronico/course/ HTTP/1.1
    Host: localhost:8001
    Content-Type: application/json

Vejamos a reposta da requisição acima:

.. code-block:: text

    HTTP/1.0 201 CREATED
    Content-Type: application/json

.. code-block:: json

    { 
      "course_resource_uri": "/solaredx/api/v1/course/5546432f43533130322f323031342e32/"
    }

Desalocando um usuário em um curso
""""""""""""""""""""""""""""""""""

Para desalocar (desmatricular) um usuário em um curso, deve-se fazer uma 
requisição ``HTTP`` ``POST`` para a URI ``/api/v1/user/<username>/course/`` 
com os campos ``course_id`` e ``action`` (com o valor ``remove``). Essa 
chamada é similar a de matrícula. Veja o exemplo abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/user/ptronico/course/ -X DELETE --header 'Content-Type: application/json' --data '{ "course_resource_uri": "/solaredx/api/v1/course/5546432f43533130322f323031342e32/" }'

.. code-block:: text

    DELETE /solaredx/api/v1/user/ptronico/course/ HTTP/1.1
    Host: localhost:8001
    Content-Type: application/json

Vejamos a reposta da requisição acima (essa resposta não retorna dados  ):

.. code-block:: text

    HTTP/1.0 204 NO CONTENT
    Content-Type: text/html; charset=utf-8

Gestão de Cursos
----------------

Essa sessão apresenta como gerenciar cursos.

Consulta e listagem de cursos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Para listar cursos acesse a URI ``/solaredx/api/v1/course/``. Veja o exemplo
abaixo:

.. code-block:: bash

    $ curl http://localhost:8001/solaredx/api/v1/course/    

O JSON retornado segue abaixo:

.. code-block:: text

    HTTP/1.0 200 OK
    Content-Type: application/json

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
                "course_absolute_url": "http://solaredx.virtual.ufc.br/courses/UFC/CS101/2013_Fall/about",
                "course_absolute_url_lms": "http://solaredx.virtual.ufc.br/courses/UFC/CS101/2013_Fall/info",
                "course_absolute_url_studio": "http://solaredxstd.virtual.ufc.br/course/UFC.CS101.2013_Fall/branch/draft/block/2013_Fall",
                "course_id": "UFC/CS101/2013_Fall",
                "display_name": "Introduction to Computer Science",
                "end": "Fri, 1 Nov 2013 12:00:00 -0300",
                "enrollment_end": "Fri, 25 Oct 2013 23:30:00 -0300",
                "enrollment_start": "Mon, 21 Oct 2013 00:00:00 -0300",
                "resource_uri": "/solaredx/api/v1/course/5546432f43533130312f323031335f46616c6c/",
                "start": "Mon, 28 Oct 2013 08:00:00 -0300"
            },
            {
                "course_absolute_url": "http://solaredx.virtual.ufc.br/courses/UFC/CS102/2014.2/about",
                "course_absolute_url_lms": "http://solaredx.virtual.ufc.br/courses/UFC/CS102/2014.2/info",
                "course_absolute_url_studio": "http://solaredxstd.virtual.ufc.br/course/UFC.CS102.2014.2/branch/draft/block/2014.2",
                "course_id": "UFC/CS102/2014.2",
                "display_name": "Teste de cria\u00e7\u00e3o de curso",
                "end": null,
                "enrollment_end": null,
                "enrollment_start": null,
                "resource_uri": "/solaredx/api/v1/course/5546432f43533130322f323031342e32/",
                "start": "Wed, 31 Dec 1969 21:00:00 -0300"
            }
        ]
    }


Criação e exclusão de cursos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Criação
"""""""

Requisição:

.. code-block:: bash
    
    $ curl http://localhost:8001/solaredx/api/v1/course/ -X POST --header 'Content-Type: application/json' --data '{ "course_creator_username": "ptronico", "course_id": "UFC/C005/2014.1", "display_name": "Novo Curso" }'

Resposta:

.. code-block:: text

    HTTP/1.0 201 CREATED
    Content-Type: application/json

.. code-block:: json

    {
        "course_creator_username": "ptronico",
        "course_id": "UFC/C005/2014.1",
        "display_name": "Novo Curso"
    }

Exclusão
""""""""

Requisição:

.. code-block:: bash
    
    $ curl http://localhost:8001/solaredx/api/v1/course/5546432f433030312f323031342e31/ -X DELETE --header 'Content-Type: application/json' --data '{ "confirm": true }'

Resposta (não são retornado dados):

.. code-block:: text

    HTTP/1.0 204 NO CONTENT
    Content-Type: text/html; charset=utf-8


Alocação e desalocação de professores e tutores em cursos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As operações de consulta de professores e tutores alocados em um curso, bem
como as requisições de alocação e desalocação de professores e tutores são
idênticas, diferenciando apenas o `endpoint`, sendo o 
``instructor_resource_uri`` para operações com Professores e o
``staff_resource_uri`` para operações com Tutores.

.. note ::

    Entende-se por `instructor` o Professor e `staff` o Tutor.

Consultando professores e tutores alocados em um curso
""""""""""""""""""""""""""""""""""""""""""""""""""""""

Requisição:

.. code-block:: bash

    $ http://localhost:8001/solaredx/api/v1/course/5546432f43543130312f323031345f3031/staff/

Resposta:

.. code-block:: text

    HTTP/1.0 200 OK
    Content-Type: application/json    

.. code-block:: json

    [
        "/solaredx/api/v1/user/ptronico/"
    ]

Alocando professores e tutores em um curso
""""""""""""""""""""""""""""""""""""""""""

Para alocar um usuário como professor ou tutor em um curso, deve-se fazer uma 
requisição ``HTTP`` ``POST`` para uma das URIs dos campos 
``instructor_resource_uri`` ou ``staff_resource_uri``. Deve-se enviar os campos
``course_id`` e ``action`` (com o valor ``add`` para adicionar ou ``remove``
para remover).

No exemplo abaixo iremos alocar um 'Professor' em um curso:

.. code-block:: bash

    $ http://localhost:8001/solaredx/api/v1/course/5546432f43543130312f323031345f3031/staff/ -X POST --header 'Content-Type: application/json' --data '{ "user_resource_uri": "/solaredx/api/v1/ptronico/" }'

O retorno ...

.. code-block:: text

    HTTP/1.0 201 CREATED
    Content-Type: application/json    

.. code-block:: json

    { 
      "user_resource_uri": "/solaredx/api/v1/ptronico/"
    }

.. note::
    Se você tentar alocar um professor ou tutor que já esteja alocado, você 
    receberá uma resposta ``400 BAD REQUEST``.

Desalocando professores e tutores em um curso
"""""""""""""""""""""""""""""""""""""""""""""

Requisição:

.. code-block:: bash

    $ http://localhost:8001/solaredx/api/v1/course/5546432f43543130312f323031345f3031/staff/ -X DELETE --header 'Content-Type: application/json' --data '{ "user_resource_uri": "/solaredx/api/v1/ptronico/" }'

Resposta (não retorna dados):

.. code-block:: text

    HTTP/1.0 204 NO CONTENT
    Content-Type: text/html; charset=utf-8
