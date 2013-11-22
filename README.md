django-solaredx
===============

Django app to provide an EDX API for integrating with Solar 2.

Quick start
-----------

1. Install django-solaredx using pip:

    pip install git+git://github.com/ptronico/django-solaredx.git

2. Add "solaredx" to your INSTALLED_APPS setting like this:

    INSTALLED_APPS += ('solaredx_api', )

3. Include the polls URLconf in your project urls.py like this:

    url(r'^solaredx/', include('solaredx.urls'))

4. Visit http://localhost:8000/solaredx/api/dev/.