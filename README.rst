.. image:: https://travis-ci.org/ecometrica/django-multisite.svg?branch=master
    :target: https://travis-ci.org/ecometrica/django-multisite?branch=master
.. image:: https://coveralls.io/repos/github/ecometrica/django-multisite/badge.svg?branch=master
    :target: https://coveralls.io/github/ecometrica/django-multisite?branch=master


README
======

Install with pip::

    pip install django-multisite


Or get the code via git::

    git clone git://github.com/ecometrica/django-multisite.git django-multisite

Then run::

    python setup.py install

Or add the django-multisite/multisite folder to your PYTHONPATH.

If you wish to contribute, instead run::

    python setup.py develop


Quickstart
----------

Replace your SITE_ID in settings.py to::

    from multisite import SiteID
    SITE_ID = SiteID(default=1)

Add these to your INSTALLED_APPS::

    INSTALLED_APPS = [
        ...
        'django.contrib.sites',
        'multisite',
        ...
    ]

Add to your settings.py TEMPLATES loaders in the OPTIONS section::

    TEMPLATES = [
        ...
        {
            ...
            'DIRS': {...}
            'OPTIONS': {
                'loaders': (
                    'multisite.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                )
            }
            ...
        }
        ...
    ]

Edit settings.py MIDDLEWARE (MIDDLEWARE_CLASSES for Django < 1.10)::

    MIDDLEWARE = (
        ...
        'multisite.middleware.DynamicSiteMiddleware',
        ...
    )

Append to settings.py, in order to use a custom cache that can be
safely cleared::

    # The cache connection to use for django-multisite.
    # Default: 'default'
    CACHE_MULTISITE_ALIAS = 'multisite'
    
    # The cache key prefix that django-multisite should use.
    # If not set, defaults to the KEY_PREFIX used in the defined
    # CACHE_MULTISITE_ALIAS or the default cache (empty string if not set)
    CACHE_MULTISITE_KEY_PREFIX = ''

If you have set CACHE\_MULTISITE\_ALIAS to a custom value, *e.g.*
``'multisite'``, add a separate backend to settings.py CACHES::

    CACHES = {
        'default': {
            ...
        },
        'multisite': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 60 * 60 * 24,  # 24 hours
            ...
        },
    }


Multisite determines the ALLOWED_HOSTS by checking all Alias domains.  You can
also set the MULTISITE_EXTRA_HOSTS to include additional hosts.  This can
include wildcards.::

    MULTISITE_EXTRA_HOSTS = ['example.com']
    # will match the single additional host

    MULTISITE_EXTRA_HOSTS = ['.example.com']
    # will match any host ending '.example.com'


Development Environments
------------------------
Multisite returns a valid Alias when in "development mode" (defaulting to the
alias associated with the default SiteID.

Development mode is either:
    - Running tests, i.e. manage.py test
    - Running locally in settings.DEBUG = True, where the hostname is a top-level name, i.e. localhost

In order to have multisite use aliases in local environments, add entries to
your local etc/hosts file to match aliases in your applications.  E.g. ::

    127.0.0.1 example.com
    127.0.0.1 examplealias.com

And access your application at example.com:8000 or examplealias.com:8000 instead of
the usual localhost:8000.


Domain fallbacks
----------------

By default, if the domain name is unknown, multisite will respond with
an HTTP 404 Not Found error. To change this behaviour, add to
settings.py::

    # The view function or class-based view that django-multisite will
    # use when it cannot match the hostname with a Site. This can be
    # the name of the function or the function itself.
    # Default: None
    MULTISITE_FALLBACK = 'django.views.generic.base.RedirectView

    # Keyword arguments for the MULTISITE_FALLBACK view.
    # Default: {}
    MULTISITE_FALLBACK_KWARGS = {'url': 'http://example.com/',
                                 'permanent': False}

Templates
---------
If required, create template subdirectories for domain level templates (in a
location specified in settings.TEMPLATES['DIRS'].

Multisite's template loader will look for templates in folders with the names of
domains, such as::

    templates/example.com


The template loader will also look for templates in a folder specified by the
optional MULTISITE_DEFAULT_TEMPLATE_DIR setting, e.g.::

    templates/multisite_templates


Cross-domain cookies
--------------------

In order to support `cross-domain cookies`_,
for purposes like single-sign-on,
prepend the following to the top of
settings.py MIDDLEWARE (MIDDLEWARE_CLASSES for Django < 1.10)::

    MIDDLEWARE = (
        'multisite.middleware.CookieDomainMiddleware',
        ...
    )

CookieDomainMiddleware will consult the `Public Suffix List`_
for effective top-level domains.
It caches this file
in the system's default temporary directory
as ``effective_tld_names.dat``.
To change this in settings.py::

    MULTISITE_PUBLIC_SUFFIX_LIST_CACHE = '/path/to/multisite_tld.dat'

By default,
any cookies without a domain set
will be reset to allow \*.domain.tld.
To change this in settings.py::

    MULTISITE_COOKIE_DOMAIN_DEPTH = 1  # Allow only *.subdomain.domain.tld

In order to fetch a new version of the list,
run::

    manage.py update_public_suffix_list

.. _cross-domain cookies: http://en.wikipedia.org/wiki/HTTP_cookie#Domain_and_Path
.. _Public Suffix List: http://publicsuffix.org/


Tests
-----

To run the tests::

    python setup.py test

Or::

    pytest

Before deploying a change, to verify it has not broken anything by running::

    tox

This runs the tests under every supported combination of Django and Python.