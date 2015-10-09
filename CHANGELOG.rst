=============
Release Notes
=============

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
