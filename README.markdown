README
======

Get the code via git:

    git clone git://github.com/plazix/django-multisite.git django-multisite

Add the django-multisite/multisite folder to your PYTHONPATH.

Replace your SITE_ID in settings.py to:

    from multisite import SiteID
    SITE_ID = SiteID()

Add to settings.py TEMPLATE_LOADERS: 

    TEMPLATE_LOADERS = ( 
        'multisite.template_loader.Loader',
        'django.template.loaders.app_directories.Loader',
    ) 

Edit to settings.py MIDDLEWARE_CLASSES:

    MIDDLEWARE_CLASSES = (
        ...
        'multisite.middleware.DynamicSiteMiddleware',
        ...
    )

Append to settings.py, in order to use a custom cache that can be
safely cleared:

    # The cache connection to use for django-multisite.
    # Default: 'default'
    CACHE_MULTISITE_ALIAS = 'multisite'
    
    # The cache key prefix that django-multisite should use.
    # Default: '' (Empty string)
    CACHE_MULTISITE_KEY_PREFIX = ''

If you have set CACHE\_MULTISITE\_ALIAS to a custom value, _e.g._
`'multisite'`, add a separate backend to settings.py CACHES:

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

Create a directory settings.TEMPLATE_DIRS directory with the names of domains, such as:

    mkdir templates/example.com


