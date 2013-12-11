django-solaredx
===============

Django app to provide an EDX API for integrating with Solar 2.

Quick start
-----------

1. Install django-solaredx using pip:

    pip install git+git://github.com/wwagner33/django-solaredx.git

2. Setup your settings file like this:

    INSTALLED_APPS += ('solaredx', )

    TASTYPIE_DEFAULT_FORMATS = ['json']

    TASTYPIE_DATETIME_FORMATTING = 'rfc-2822'

    SOLAREDX_SECRET_KEY = 'your secret key'

    AUTHENTICATION_BACKENDS = (
        'solaredx.backends.SolarEDXBackend',
    )    

3. Include the polls URLconf in your project urls.py like this:

    url(r'^solaredx/', include('solaredx.urls'))

4. Visit http://localhost:8000/solaredx/api/dev/.