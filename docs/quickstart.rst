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
requisição HTTP GET::

    $ curl http://localhost:8001/solaredx/api/dev/user/
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
                "course_resource_uri": "/solaredx/api/dev/user/ptronico/course/",
                "date_joined": "Wed, 2 Oct 2013 13:53:50 -0300",
                "email": "ptronico@gmail.com",
                "is_active": true,
                "name": null,
                "resource_uri": "/solaredx/api/dev/user/ptronico/",
                "username": "ptronico"
            },
            {
                "course_resource_uri": "/solaredx/api/dev/user/pedrorafa/course/",
                "date_joined": "Wed, 2 Oct 2013 13:56:31 -0300",
                "email": "pedro@pedrorafa.com",
                "is_active": true,
                "name": null,
                "resource_uri": "/solaredx/api/dev/user/pedrorafa/",
                "username": "pedrorafa"
            },
        ]
    }
