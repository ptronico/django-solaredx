.. _installing:

Instalação e Configuração
=========================

Instalar e configurar o SolarEDX na sua instalação EDX é simples. Veja abaixo:

Instalação
----------

1. Instale a dependência abaixo:

 * django-tastypie 0.9.16 (https://github.com/toastdriven/django-tastypie/tree/v0.9.16)

 .. note::

    Observe que a versão do Tastypie (django-tastypie) não é a mais 
    recente. Isso ocorre porquê, na época do desenvolvimento do SolarEDX, 
    o EDX utilizava o Django 1.4 (a qual é suportada apenas pelo Tastypie 
    0.9.16 ou anteriores).

2. Instale o SolarEDX a partir do GitHub.

 .. code-block:: bash

    $ pip install git+git://github.com/wwagner33/django-solaredx.git

.. _conf:

Configuração
------------

Siga os passos abaixo para configuração do SolarEDX na instalação do EDX:

1. Inclua as variáveis abaixo no arquivo de configuração do CMS:
    
 .. code-block:: python

    AUTHENTICATION_BACKENDS = ('solaredx.backends.SolarEDXBackend', )

    INSTALLED_APPS += ('tastypie', 'solaredx', )

    TASTYPIE_DEFAULT_FORMATS = ['json']

    TASTYPIE_DATETIME_FORMATTING = 'rfc-2822'

    SOLAREDX_SECRET_KEY = 'your secret key'

2. Inclua as URLs do SolarEDX no arquivo de configuração de URLs do CMS:

 .. code-block:: python

    url(r'^solaredx/', include('solaredx.urls'))
