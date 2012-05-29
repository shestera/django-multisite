# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import get_cache
from django.db.models.signals import pre_save, post_delete
from django.utils.hashcompat import md5_constructor


class DynamicSiteMiddleware(object):
    def __init__(self):
        self.cache_alias = getattr(settings, 'CACHE_MULTISITE_ALIAS',
                                   'default')
        self.key_prefix = getattr(settings, 'CACHE_MULTISITE_KEY_PREFIX',
                                  '')
        self.cache = get_cache(self.cache_alias)
        pre_save.connect(self.site_domain_changed_hook, sender=Site)
        post_delete.connect(self.site_deleted_hook, sender=Site)

    def get_cache_key(self, host):
        """Returns a cache key based on ``host``."""
        host = md5_constructor(host)
        return 'multisite.site_id.%s.%s' % (self.key_prefix, host.hexdigest())

    def process_request(self, request):
        host = request.get_host()
        shost = host.rsplit(':', 1)[0] # only host, without port
        cache_key = self.get_cache_key(host)

        site_id = self.cache.get(cache_key)
        if site_id is not None:
            settings.SITE_ID.set(site_id)
            return

        try: # get by whole hostname
            site = Site.objects.get(domain=host)
            self.cache.set(cache_key, site.pk)
            settings.SITE_ID.set(site.pk)
            return
        except Site.DoesNotExist:
            pass

        if shost != host: # get by hostname without port
            try:
                site = Site.objects.get(domain=shost)
                self.cache.set(cache_key, site.pk)
                settings.SITE_ID.set(site.pk)
                return
            except Site.DoesNotExist:
                pass

        try: # get by settings.SITE_ID
            site = Site.objects.get(pk=settings.SITE_ID)
            self.cache.set(cache_key, site.pk)
            return
        except Site.DoesNotExist:
            pass

        try: # misconfigured settings?
            site = Site.objects.all()[0]
            self.cache.set(cache_key, site.pk)
            settings.SITE_ID.set(site.pk)
            return
        except IndexError: # no sites in db
            pass

    def site_domain_changed_hook(self, sender, instance, raw, *args, **kwargs):
        """Clears the cache if Site.domain has changed."""
        if raw:
            return
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.domain != instance.domain:
                self.cache.clear()
        except sender.DoesNotExist:
            pass

    def site_deleted_hook(self, *args, **kwargs):
        """Clears the cache if Site was deleted."""
        self.cache.clear()