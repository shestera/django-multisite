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

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
