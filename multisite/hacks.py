import sys

from django.conf import settings


def use_framework_for_site_cache():
    """Patches sites app to use the caching framework instead of a dict."""
    from django.contrib.sites import models
    from django.core.cache import get_cache

    # Patch the SITE_CACHE
    cache_alias = getattr(settings, 'CACHE_MULTISITE_ALIAS', 'default')
    key_prefix = getattr(settings, 'CACHE_MULTISITE_KEY_PREFIX', '')
    models.SITE_CACHE = DictCache(get_cache(backend=cache_alias,
                                            KEY_PREFIX=key_prefix))

    # Patch the SiteManager class
    models.SiteManager.clear_cache = SiteManager_clear_cache


# Override SiteManager.clear_cache so it doesn't clobber SITE_CACHE
def SiteManager_clear_cache(self):
    """Clears the ``Site`` object cache."""
    models = sys.modules.get(self.__class__.__module__)
    models.SITE_CACHE.clear()


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
