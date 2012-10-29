# -*- coding: utf-8 -*-
from urlparse import urlsplit, urlunsplit

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import get_cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import get_callable
from django.db.models.signals import pre_save, post_delete
from django.http import Http404, HttpResponsePermanentRedirect
from django.utils.hashcompat import md5_constructor

from .models import Alias


class DynamicSiteMiddleware(object):
    def __init__(self):
        if not hasattr(settings.SITE_ID, 'set'):
            raise TypeError('Invalid type for settings.SITE_ID: %s' %
                            type(settings.SITE_ID).__name__)

        self.cache_alias = getattr(settings, 'CACHE_MULTISITE_ALIAS',
                                   'default')
        self.key_prefix = getattr(settings, 'CACHE_MULTISITE_KEY_PREFIX',
                                  '')
        self.cache = get_cache(self.cache_alias, KEY_PREFIX=self.key_prefix)
        pre_save.connect(self.site_domain_changed_hook, sender=Site)
        post_delete.connect(self.site_deleted_hook, sender=Site)

    def get_cache_key(self, netloc):
        """Returns a cache key based on ``netloc``."""
        netloc = md5_constructor(netloc)
        return 'multisite.alias.%s.%s' % (self.key_prefix,
                                          netloc.hexdigest())

    def netloc_parse(self, netloc):
        """
        Returns ``(host, port)`` for ``netloc`` of the form ``'host:port'``.

        If netloc does not have a port number, ``port`` will be None.
        """
        if ':' in netloc:
            return netloc.rsplit(':', 1)
        else:
            return netloc, None

    def get_development_alias(self, netloc):
        """
        Returns valid Alias when in development mode. Otherwise, returns None.

        Development mode is either:
        - Running tests, i.e. manage.py test
        - Running locally in settings.DEBUG = True, where the hostname is
          a top-level name, i.e. localhost
        """
        # When running tests, django.core.mail.outbox exists and
        # netloc == 'testserver'
        is_testserver = (hasattr(mail, 'outbox') and
                         netloc in ('testserver', 'adminsite.com'))
        # When using runserver, assume that host will only have one path
        # component. This covers 'localhost' and your machine name.
        is_local_debug = (settings.DEBUG and len(netloc.split('.')) == 1)
        if is_testserver or is_local_debug:
            try:
                # Prefer the default SITE_ID
                site_id = settings.SITE_ID.get_default()
                return Alias.canonical.get(site=site_id)
            except ValueError:
                # Fallback to the first Site object
                return Alias.canonical.order_by('site')[0]

    def get_alias(self, netloc):
        """
        Returns Alias matching ``netloc``. Otherwise, returns None.
        """
        host, port = self.netloc_parse(netloc)

        try:
            alias = Alias.objects.resolve(host=host, port=port)
        except ValueError:
            alias = None

        if alias is None:
            # Running under TestCase or runserver?
            return self.get_development_alias(netloc)
        return alias

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

    def redirect_to_canonical(self, request, alias):
        if not alias.redirect_to_canonical or alias.is_canonical:
            return
        url = urlsplit(request.build_absolute_uri(request.get_full_path()))
        url = urlunsplit((url.scheme,
                          alias.site.domain,
                          url.path, url.query, url.fragment))
        return HttpResponsePermanentRedirect(url)

    def process_request(self, request):
        netloc = request.get_host().lower()
        cache_key = self.get_cache_key(netloc)

        # Find the Alias in the cache
        alias = self.cache.get(cache_key)
        if alias is not None:
            self.cache.set(cache_key, alias)
            settings.SITE_ID.set(alias.site_id)
            return self.redirect_to_canonical(request, alias)

        # Cache missed
        alias = self.get_alias(netloc)

        # Fallback using settings.MULTISITE_FALLBACK
        if alias is None:
            settings.SITE_ID.reset()
            return self.fallback_view(request)

        # Found Site
        self.cache.set(cache_key, alias)
        settings.SITE_ID.set(alias.site_id)
        return self.redirect_to_canonical(request, alias)

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
