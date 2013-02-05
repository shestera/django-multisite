README
======

Get the code via git:

    git clone git://github.com/shestera/django-multisite.git django-multisite

Add the django-multisite/multisite folder to your PYTHONPATH.

Replace your SITE_ID in settings.py to:

    from multisite.threadlocals import SiteIDHook
    SITE_ID = SiteIDHook()

Add to settings.py TEMPLATE_LOADERS: 

    TEMPLATE_LOADERS = ( 
        'multisite.template_loader.load_template_source',
        'django.template.loaders.app_directories.load_template_source', 
    ) 

Edit to settings.py MIDDLEWARE_CLASSES:

    MIDDLEWARE_CLASSES = (
        ...
        'multisite.middleware.DynamicSiteMiddleware',
        ...
    )

Create a directory settings.TEMPLATE_DIRS directory with the names of domains, such as:

    mkdir templates/example.com


