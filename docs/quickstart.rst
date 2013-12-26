.. _quickstart:

Quickstart
==========

Pronto para começar? Essa página dará uma boa introdução para se começar a 
usar o SolarEDX. Assumiremos que você já tem o SolarEDX instalado na sua
instalação do EDX.

Vamos começar com alguns exemplos simples...

Listando usuários
-----------------

A API provida pelo SolarEDX permite a listagem de usuários através de uma
requisição HTTP GET. Utilizaremos o ``curl`` para fazer uma requisição via
terminal: ::

    $ curl http://localhost:8001/solaredx/api/dev/user/

A API retorna dados serializados em JSON. A estrutura básica de um `endpoint`
de listagem de objetos retorna dois campos: ``meta`` e ``objects``. O primeiro, 
é responsável por trazer metadados sobre os objetos. O segundo retornar uma 
lista de objetos, no caso, de usuários. Veja o resultado da requisição: ::

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 3
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
            },
            {
                "date_joined": "Tue, 26 Nov 2013 11:46:11 -0300",
                "email": "contato@nungo.com.br",
                "is_active": false,
                "name": null,
                "resource_uri": "/solaredx/api/dev/user/nungo/",
                "username": "nungo"
            }
        ]
    }

Consultando um usuário
----------------------

Perceba que em cada objeto listado na resposta acima há um campo chamado 
``resource_uri``. Esse campo fornece a URI de acesso ao objeto. Faremos agora
uma requisição de leitura ao objeto `ptronico`, utilizando o endereço da URI: ::

    $ curl http://localhost:8001/solaredx/api/dev/user/ptronico/

Como se pode ver, a consulta de um objeto retorna apenas o próprio objeto, 
serializado em JSON. Veja abaixo: :: 

    {
        "course_resource_uri": "/solaredx/api/dev/user/ptronico/course/",
        "date_joined": "Wed, 2 Oct 2013 13:53:50 -0300",
        "email": "ptronico@gmail.com",
        "is_active": true,
        "name": null,
        "username": "ptronico"
    }

Consultando matrículas de um usuário
------------------------------------

Percebemos que o retorno de uma requisição ao objeto pode retornar mais 
informações do objeto do que a requisição de listagem de objetos. Por 
exemplo, o campo ``course_resource_uri`` não está presente no ``endpoint`` 
de listagem de usuários. Isso é devido à economia de banda e a simplificação
de consultas ao banco de dados.

O campo ``course_resource_uri`` retorna a URI de cursos em que o usuário está
matriculado. Para consultar em quais cursos o usuário `ptronico` está 
matriculado, basta realizar a consulta abaixo: ::

    $ curl http://localhost:8001/solaredx/api/dev/user/ptronico/course/

Segue o resultado: ::

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 1
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
                "resource_uri": "/solaredx/api/dev/course/5546432f43533130312f323031335f46616c6c/",
                "start": "Mon, 28 Oct 2013 08:00:00 -0300"
            }
        ]
    }

Os dados acima mostram que o usuário `ptronico` está matriculado apenas em um
curso, a saber, o "Introduction to Computer Science". Veja que o resultado 
também fornece as URLs absolutas e outras informações relevantes sobre o curso.

Matriculando um usuário em um curso
-----------------------------------

Para matricular ou "desmatricular" um usuário em um curso é simples. Você 
deve fazer uma requisição HTTP POST para o mesmo endpoint de consulta de 
matrículas de um usuário. Nessa requisição você deve enviar dois campos,
sendo eles ``course_id`` e ``action``. O ``course_id`` deve conter o ID do
curso em que se deseja realizar a operação. O campo ``action`` deve conter a
ação a ser realizada, podendo ser uma das duas: ``add`` (matricula) ou 
``remove`` (desmatricula). O retorno dessa requisição será sempre ou o objeto
curso em questão quando a operação ocorrer com sucesso ou um JSON contendo 
``{ "status": "error" }`` quando houver algum erro e a operação não for 
realizada.

Na requisição abaixo iremos matricular o usuário no curso 
``UFC/CT101/2014_01``: ::

    $ curl http://localhost:8001/solaredx/api/dev/user/ptronico/course/ --data "course_id=UFC/CT101/2014_01&action=add"

Conforme esperado, a requisição retornou o objeto do curso em que o usuário 
foi matriculado. Veja abaixo o retorno da requisição: ::

    {
        "course_absolute_url": "http://solaredx.virtual.ufc.br/courses/UFC/CT101/2014_01/about",
        "course_absolute_url_lms": "http://solaredx.virtual.ufc.br/courses/UFC/CT101/2014_01/info",
        "course_absolute_url_studio": "http://solaredxstd.virtual.ufc.br/course/UFC.CT101.2014_01/branch/draft/block/2014_01",
        "course_id": "UFC/CT101/2014_01",
        "display_name": "Curso TESTE",
        "end": null,
        "enrollment_end": null,
        "enrollment_start": null,
        "instructor_resource_uri": "/solaredx/api/dev/course/5546432f43543130312f323031345f3031/instructor/",
        "staff_resource_uri": "/solaredx/api/dev/course/5546432f43543130312f323031345f3031/staff/",
        "start": "Wed, 31 Dec 1969 21:00:00 -0300"
    }

Por fim, vamos listar todos os cursos em que o usuário está matriculado apenas 
para confirmar que a operação foi realizada com sucesso: ::

    $ curl http://localhost:8001/solaredx/api/dev/user/ptronico/course/

A listagem retornada comprova que o usuário `ptronico` está agora matriculado
também no curso ``UFC/CT101/2014_01``. Veja o JSON retornado: ::

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
                "resource_uri": "/solaredx/api/dev/course/5546432f43533130312f323031335f46616c6c/",
                "start": "Mon, 28 Oct 2013 08:00:00 -0300"
            },
            {
                "course_absolute_url": "http://solaredx.virtual.ufc.br/courses/UFC/CT101/2014_01/about",
                "course_absolute_url_lms": "http://solaredx.virtual.ufc.br/courses/UFC/CT101/2014_01/info",
                "course_absolute_url_studio": "http://solaredxstd.virtual.ufc.br/course/UFC.CT101.2014_01/branch/draft/block/2014_01",
                "course_id": "UFC/CT101/2014_01",
                "display_name": "Curso TESTE",
                "end": null,
                "enrollment_end": null,
                "enrollment_start": null,
                "resource_uri": "/solaredx/api/dev/course/5546432f43543130312f323031345f3031/",
                "start": "Wed, 31 Dec 1969 21:00:00 -0300"
            }
        ]
    }

Observações finais
------------------

Nesse artigo buscamos fazer uma apresentação rápida de como a API funciona.
Os princípios que nortearam as operações acima também norteiam outras 
operações da API. Em outras seções dessa documentação você encontrará 
informações mais específicas e detalhadas sobre outros ``endpoints`` da API.


