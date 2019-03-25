from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from django.conf import settings
from django.db.models.signals import post_save, post_delete


def use_framework_for_site_cache():
    """Patches sites app to use the caching framework instead of a dict."""
    # This patch has to exist because SITE_CACHE is normally a dict,
    # which is local only to the process. When running multiple
    # processes, a change to a Site will not be reflected across other
    # ones.
    from django.contrib.sites import models

    # Patch the SITE_CACHE
    site_cache = SiteCache()
    models.SITE_CACHE = DictCache(site_cache)

    # Patch the SiteManager class
    models.SiteManager.clear_cache = SiteManager_clear_cache
    models.SiteManager._get_site_by_id = SiteManager_get_site_by_id

    # Hooks to update SiteCache
    post_save.connect(site_cache._site_changed_hook, sender=models.Site)
    post_delete.connect(site_cache._site_deleted_hook, sender=models.Site)


# Override SiteManager.clear_cache so it doesn't clobber SITE_CACHE
def SiteManager_clear_cache(self):
    """Clears the ``Site`` object cache."""
    models = sys.modules.get(self.__class__.__module__)
    models.SITE_CACHE.clear()


# Override SiteManager._get_site_by_id
def SiteManager_get_site_by_id(self, site_id):
    """
    Patch _get_site_by_id to retrieve the site from the cache at the
    beginning of the method to avoid a race condition.
    """
    models = sys.modules.get(self.__class__.__module__)
    site = models.SITE_CACHE.get(site_id)
    if site is None:
        site = self.get(pk=site_id)
        models.SITE_CACHE[site_id] = site
    return site


class SiteCache(object):
    """Wrapper for SITE_CACHE that assigns a key_prefix."""

    def __init__(self, cache=None):
        from django.core.cache import caches

        if cache is None:
            cache_alias = getattr(settings, 'CACHE_MULTISITE_ALIAS', 'default')
            self._key_prefix = getattr(
                settings,
                'CACHE_MULTISITE_KEY_PREFIX',
                settings.CACHES[cache_alias].get('KEY_PREFIX', '')
            )
            cache = caches[cache_alias]
        else:
            self._key_prefix = getattr(
                settings, 'CACHE_MULTISITE_KEY_PREFIX', cache.key_prefix
            )
        self._cache = cache

    def _get_cache_key(self, key):
        return 'sites.%s.%s' % (self.key_prefix, key)

    def _clean_site(self, site):
        # Force site.id to be an int, not a SiteID object.
        site.id = int(site.id)
        return site

    @property
    def key_prefix(self):
        return self._key_prefix

    def get(self, key, *args, **kwargs):
        return self._cache.get(key=self._get_cache_key(key), *args, **kwargs)

    def set(self, key, value, *args, **kwargs):
        self._cache.set(key=self._get_cache_key(key),
                        value=self._clean_site(value),
                        *args, **kwargs)

    def delete(self, key, *args, **kwargs):
        self._cache.delete(key=self._get_cache_key(key), *args, **kwargs)

    def __contains__(self, key, *args, **kwargs):
        return self._cache.__contains__(key=self._get_cache_key(key),
                                        *args, **kwargs)

    def clear(self, *args, **kwargs):
        self._cache.clear(*args, **kwargs)

    def _site_changed_hook(self, sender, instance, raw, *args, **kwargs):
        if raw:
            return
        self.set(key=instance.pk, value=instance)

    def _site_deleted_hook(self, sender, instance, *args, **kwargs):
        self.delete(key=instance.pk)


class DictCache(object):
    """Add dictionary protocol to django.core.cache.backends.BaseCache."""

    def __init__(self, cache):
        self._cache = cache

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        hash(key)               # Raise TypeError if unhashable
        result = self._cache.get(key=key)
        if result is None:
            raise KeyError(key)
        return result

    def __setitem__(self, key, value):
        """x.__setitem__(i, y) <==> x[i]=y"""
        hash(key)               # Raise TypeError if unhashable
        self._cache.set(key=key, value=value)

    def __delitem__(self, key):
        """x.__delitem__(y) <==> del x[y]"""
        hash(key)               # Raise TypeError if unhashable
        self._cache.delete(key=key)

    def __contains__(self, item):
        """D.__contains__(k) -> True if D has a key k, else False"""
        hash(item)              # Raise TypeError if unhashable
        return self._cache.__contains__(key=item)

    def clear(self):
        """D.clear() -> None.  Remove all items from D."""
        self._cache.clear()

    def get(self, key, default=None, version=None):
        """D.key(k[, d]) -> k if D has a key k, else d. Defaults to None"""
        hash(key)               # Raise TypeError if unhashable
        return self._cache.get(key=key, default=default, version=version)
