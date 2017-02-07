import django

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

from multisite import SiteID
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
# Default: 'default'
CACHE_MULTISITE_ALIAS = 'default'

# The cache key prefix that django-multisite should use.
# Default: '' (Empty string)
CACHE_MULTISITE_KEY_PREFIX = ''

# FIXME: made redundant by override_settings in some of the tests; this should be harmonized.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
    },
}


if django.VERSION < (1, 6):
    # FIXME: is this still relevant? are we still supporting this?
    # See https://github.com/ecometrica/django-multisite/issues/39
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

