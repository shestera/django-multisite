=============
Release Notes
=============

1.2.2
-----

* Fix for 1.9: change the return type of filesystem template loader's get_template_sources()

1.2.1
-----

* Remove django.utils.unittest (deprecated in 1.9)
* Use post_migrate instead of post_syncdb in > 1.7

1.2.0
-----

* We now support Django 1.9
* Following deprecation in django, all get_cache methods have been replaced caches.

1.1.0
-----

* We now support post-South Django 1.7 native migrations.

1.0.0
-----

* 1.0 release. API stability promised from now on.
* Following the deprecation in Django itself, all get_query_set methods have been renamed to get_queryset. This means Django 1.6 is now the minimum required version.

0.5.1
-----

* Add key prefix tests

0.5.0
-----

* Allow use of cache key prefixes from the CACHES settings if CACHE_MULTISITE_KEY_PREFIX not set
