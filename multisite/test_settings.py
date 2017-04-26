import django
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


TEST_RUNNER = 'django.test.runner.DiscoverRunner'
