import django
import os
from multisite import SiteID

SECRET_KEY = "iufoj=mibkpdz*%bob952x(%49rqgv8gg45k36kjcg76&-y5=!"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
    }
}

INSTALLED_APPS = [
    'django.contrib.sites',
    'multisite',
]


SITE_ID = SiteID(default=1)

MIDDLEWARE = [
    'multisite.middleware.DynamicSiteMiddleware',
]
if django.VERSION < (1,10,0):
    # we are backwards compatible, but the settings file format has changed post-1.10:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    MIDDLEWARE_CLASSES = list(MIDDLEWARE)
    del MIDDLEWARE

# The cache connection to use for django-multisite.
CACHE_MULTISITE_ALIAS = 'test_multisite'

CACHES = {
    # default cache required for Django <= 1.8
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
    CACHE_MULTISITE_ALIAS: {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
        'KEY_PREFIX': 'looselycoupled',
    },
}

MULTISITE_EXTRA_HOSTS = ['.extrahost.com']

if django.VERSION < (1, 8):
    TEMPLATE_LOADERS = ['multisite.template.loaders.filesystem.Loader']
    TEMPLATE_DIRS = [os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  'test_templates')]
else:
   TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(os.path.abspath(os.path.dirname(__file__)),
                             'test_templates')
            ],
            'OPTIONS': {
                'loaders': [
                    'multisite.template.loaders.filesystem.Loader',
                ]
            },
        }
    ]


TEST_RUNNER = 'django.test.runner.DiscoverRunner'
