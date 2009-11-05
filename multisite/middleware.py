# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site

HOST_CACHE = {}

class DynamicSiteMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        shost = host.rsplit(':', 1)[0] # only host, without port

        try:
            settings.SITE_ID.set(HOST_CACHE[host])
            return
        except KeyError:
            pass

        try: # get by whole hostname
            site = Site.objects.get(domain=host)
            HOST_CACHE[host] = site.pk
            settings.SITE_ID.set(site.pk)
            return
        except Site.DoesNotExist:
            pass

        if shost != host: # get by hostname without port
            try:
                site = Site.objects.get(domain=shost)
                HOST_CACHE[host] = site.pk
                settings.SITE_ID.set(site.pk)
                return
            except Site.DoesNotExist:
                pass

        try: # get by settings.SITE_ID
            site = Site.objects.get(pk=settings.SITE_ID)
            HOST_CACHE[host] = site.pk
            return
        except Site.DoesNotExist:
            pass

        try: # misconfigured settings?
            site = Site.objects.all()[0]
            HOST_CACHE[host] = site.pk
            settings.SITE_ID.set(site.pk)
            return
        except IndexError: # no sites in db
            pass
