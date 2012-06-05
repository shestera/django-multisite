import sys

from django.conf import settings


def use_framework_for_site_cache():
    """Patches sites app to use the caching framework instead of a dict."""
    from django.contrib.sites import models

    # Patch the SITE_CACHE
    models.SITE_CACHE = DictCache(SiteCache())

    # Patch the SiteManager class
    models.SiteManager.clear_cache = SiteManager_clear_cache


# Override SiteManager.clear_cache so it doesn't clobber SITE_CACHE
def SiteManager_clear_cache(self):
    """Clears the ``Site`` object cache."""
    models = sys.modules.get(self.__class__.__module__)
    models.SITE_CACHE.clear()


class SiteCache(object):
    """Wrapper for SITE_CACHE that assigns a key_prefix."""

    def __init__(self, cache=None, key_prefix=None):
        from django.core.cache import get_cache

        if key_prefix is None:
            key_prefix = getattr(settings, 'CACHE_SITES_KEY_PREFIX', '')
        self.key_prefix = key_prefix

        if cache is None:
            cache_alias = getattr(settings, 'CACHE_SITES_ALIAS', 'default')
            cache = get_cache(cache_alias, KEY_PREFIX=self.key_prefix)
        self._cache = cache

    def _get_cache_key(self, key):
        return 'sites.%s.%s' % (self.key_prefix, key)

    def get(self, key, *args, **kwargs):
        return self._cache.get(key=self._get_cache_key(key), *args, **kwargs)

    def set(self, key, value, *args, **kwargs):
        self._cache.set(key=self._get_cache_key(key), value=value,
                        *args, **kwargs)

    def delete(self, key, *args, **kwargs):
        self._cache.delete(key=self._get_cache_key(key), *args, **kwargs)

    def __contains__(self, key, *args, **kwargs):
        return self._cache.__contains__(key=self._get_cache_key(key),
                                        *args, **kwargs)

    def clear(self, *args, **kwargs):
        self._cache.clear(*args, **kwargs)


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
