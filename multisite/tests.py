from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import RequestFactory as DjangoRequestFactory
from django.utils.unittest import skipUnless

try:
    from django.test.utils import override_settings
except ImportError:
    from override_settings import override_settings

from multisite.middleware import DynamicSiteMiddleware, HOST_CACHE
from multisite.threadlocals import SiteIDHook, _thread_locals


class RequestFactory(DjangoRequestFactory):
    def __init__(self, host):
        super(RequestFactory, self).__init__()
        self.host = host

    def get(self, path, data={}, host=None, **extra):
        if host is None:
            host = self.host
        return super(RequestFactory, self).get(path=path, data=data,
                                               HTTP_HOST=host, **extra)


@skipUnless(Site._meta.installed,
            'django.contrib.sites is not in settings.INSTALLED_APPS')
@override_settings(SITE_ID=SiteIDHook())
class DynamicSiteMiddlewareTest(TestCase):
    def setUp(self):
        self.host = 'example.com'
        self.factory = RequestFactory(host=self.host)

        Site.objects.all().delete()
        self.site = Site.objects.create(domain=self.host)

        HOST_CACHE.clear()
        self.middleware = DynamicSiteMiddleware()

    def tearDown(self):
        HOST_CACHE.clear()
        try:
            del _thread_locals.SITE_ID
        except AttributeError:
            pass

    def test_valid_domain(self):
        # Make the request
        request = self.factory.get('/')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, self.site.pk)
        # Request again
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, self.site.pk)

    def test_valid_domain_port(self):
        # Make the request with a specific port
        request = self.factory.get('/', host=self.host + ':8000')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, self.site.pk)
        # Request again
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, self.site.pk)

    def test_change_domain(self):
        # Make the request
        request = self.factory.get('/')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, self.site.pk)
        # Another request with a different site
        site2 = Site.objects.create(domain='anothersite.example')
        request = self.factory.get('/', host=site2.domain)
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, site2.pk)

    def test_invalid_domain(self):
        # Make the request
        request = self.factory.get('/', host='invalid')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, Site.objects.all()[0].pk)

    def test_invalid_domain_port(self):
        # Make the request
        request = self.factory.get('/', host=':8000')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, Site.objects.all()[0].pk)

    def test_no_sites(self):
        # Remove all Sites
        Site.objects.all().delete()
        # Make the request
        request = self.factory.get('/')
        self.assertEqual(self.middleware.process_request(request), None)
        self.assertEqual(settings.SITE_ID, 1)
