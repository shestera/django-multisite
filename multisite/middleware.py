# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import get_cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable
from django.db.models.signals import pre_save, post_delete
from django.http import Http404
from django.utils.hashcompat import md5_constructor


class DynamicSiteMiddleware(object):
    def __init__(self):
        if not hasattr(settings.SITE_ID, 'set'):
            raise TypeError('Invalid type for settings.SITE_ID: %s' %
                            type(settings.SITE_ID).__name__)

        self.cache_alias = getattr(settings, 'CACHE_MULTISITE_ALIAS',
                                   'default')
        self.key_prefix = getattr(settings, 'CACHE_MULTISITE_KEY_PREFIX',
                                  '')
        self.cache = get_cache(self.cache_alias)
        pre_save.connect(self.site_domain_changed_hook, sender=Site)
        post_delete.connect(self.site_deleted_hook, sender=Site)

    def get_cache_key(self, netloc):
        """Returns a cache key based on ``netloc``."""
        netloc = md5_constructor(netloc)
        return 'multisite.site_id.%s.%s' % (self.key_prefix,
                                            netloc.hexdigest())

    def get_testserver_site(self, netloc):
        """
        Returns valid Site when running Django tests. Otherwise, returns None.
        """
        if hasattr(mail, 'outbox') and netloc == 'testserver':
            try:
                # Prefer the default SITE_ID
                site_id = settings.SITE_ID.get_default()
                return Site.objects.get(pk=site_id)
            except ValueError:
                # Fallback to the first Site object
                return Site.objects.order_by('pk')[0]

    def get_site(self, netloc):
        """
        Returns the Site that matches ``netloc``.

        ``netloc`` can be a bare hostname ``'example.com'`` or a
        hostname with a port number``'example.com:8000'``.

        Attempts to match by netloc with the port number first,
        against the domain field in Site. If that fails, it will try
        to match the bare hostname with no port number.

        All comparisons are done case-insensitively.

        """
        try:
            # Get by netloc
            return Site.objects.get(domain__iexact=netloc)
        except Site.DoesNotExist:
            host = netloc.rsplit(':', 1)[0]
            if host != netloc:
                # Get by hostname without port
                return Site.objects.get(domain__iexact=host)
            raise

    def fallback_view(self, request):
        """
        Runs the fallback view function in ``settings.MULTISITE_FALLBACK``.

        If ``MULTISITE_FALLBACK`` is None, raises an Http404 error.

        If ``MULTISITE_FALLBACK`` is callable, will treat that
        callable as a view that returns an HttpResponse.

        If ``MULTISITE_FALLBACK`` is a string, will resolve it to a
        view that returns an HttpResponse.

        In order to use a generic view that takes additional
        parameters, ``settings.MULTISITE_FALLBACK_KWARGS`` may be a
        dictionary of additional keyword arguments.
        """
        fallback = getattr(settings, 'MULTISITE_FALLBACK', None)
        if fallback is None:
            raise Http404
        if callable(fallback):
            view = fallback
        else:
            view = get_callable(fallback)
            if not callable(view):
                raise ImproperlyConfigured(
                    'settings.MULTISITE_FALLBACK is not callable: %s' %
                    fallback
                )

        kwargs = getattr(settings, 'MULTISITE_FALLBACK_KWARGS', {})
        if hasattr(view, 'as_view'):
            # Class-based view
            return view.as_view(**kwargs)(request)
        # View function
        return view(request, **kwargs)

    def process_request(self, request):
        netloc = request.get_host().lower()
        cache_key = self.get_cache_key(netloc)

        # Find the SITE_ID in the cache
        site_id = self.cache.get(cache_key)
        if site_id is not None:
            settings.SITE_ID.set(site_id)
            return

        # Cache missed
        try:
            site = self.get_site(netloc)
        except Site.DoesNotExist:
            site = self.get_testserver_site(netloc)
            if site is None:
                # Fallback using settings.MULTISITE_FALLBACK
                settings.SITE_ID.reset()
                return self.fallback_view(request)

        self.cache.set(cache_key, site.pk)
        settings.SITE_ID.set(site.pk)

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
