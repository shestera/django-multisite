=============
Release Notes
=============

1.6.0
-----
* Fix KeyError from _get_site_by_id
* Drop support for Django 1.7
* Remove unnecessary cache type warnings
* Remove deprecated SiteIDHook

1.5.0
-----
* Support Django 2.0 (PR #47 and #60)
* Remove code for Django < 1.7
* Remove obsolete PathAssistedCurrentSiteManager
* Remove obsolete template.loaders.cached
* Update README to better describe local development setup

1.4.1
-----
* Specify Django <2.0 in setup.py
* Drop support for python 3.3

1.4.0
-----
* Support Django 1.10 (PR #38) and 1.11
* Support Python 3
* Remove support for Django <1.7
* Use setuptools over distutils, and integrate the tests with them
* Use pytest and tox for testing
* Set up CI with travis
* Set up coverage and coveralls.io
* Document MULTISITE_EXTRA_HOSTS in README

1.3.1
-----

* Add default for SiteID in the README (PR #31)
* Respect the CACHE_MULTISITE_ALIAS in SiteCache (PR #34)
* Replace deprecated ExtractResult().tld with .suffic (PR #32)

1.3.0
-----

* Fix tempfile issue with update_public_suffix_list command
* Support for tldextract version >= 2.0

1.2.6
----

* Pin the tldextract dependency to version < 2.0, which breaks API.

1.2.5
----

* Make template loading more resilient to changes in django (thanks to jbazik for the contribution)

1.2.4
-----

* Fix domain validation so it's called after the pre_save signal

1.2.3
-----

* Fix a broken test, due to a django uniqueness constraint in 1.9

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
