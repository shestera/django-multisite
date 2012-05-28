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
@override_settings(SITE_ID=SiteIDHook(), DEBUG=True)
class TestContribSite(TestCase):
    def setUp(self):
        self.host = 'example.com'
        self.site = Site.objects.create(domain=self.host)
        settings.SITE_ID.set(self.site.id)

    def tearDown(self):
        try:
            del _thread_locals.SITE_ID
        except AttributeError:
            pass

    def test_get_current_site(self):
        current_site = Site.objects.get_current()
        self.assertEqual(current_site, self.site)
        self.assertEqual(current_site.id, settings.SITE_ID)


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


class TestSiteIDHook(TestCase):
    def setUp(self):
        self.host = 'example.com'

        Site.objects.all().delete()
        self.site = Site.objects.create(domain=self.host)

        self.reset_site_id()
        self.site_id = SiteIDHook()

    def tearDown(self):
        self.reset_site_id()

    def reset_site_id(self):
        try:
            del _thread_locals.SITE_ID
        except AttributeError:
            pass

    def test_compare_default_site_id(self):
        # Default SITE_ID is 1
        self.assertEqual(self.site_id, 1)
        self.assertFalse(self.site_id != 1)
        self.assertFalse(self.site_id < 1)
        self.assertTrue(self.site_id <= 1)
        self.assertFalse(self.site_id > 1)
        self.assertTrue(self.site_id >= 1)

    def test_compare_site_ids(self):
        self.site_id.set(1)
        self.assertEqual(self.site_id, self.site_id)
        self.assertFalse(self.site_id != self.site_id)
        self.assertFalse(self.site_id < self.site_id)
        self.assertTrue(self.site_id <= self.site_id)
        self.assertFalse(self.site_id > self.site_id)
        self.assertTrue(self.site_id >= self.site_id)

    def test_compare_differing_types(self):
        self.site_id.set(1)
        # SiteIDHook <op> int
        self.assertNotEqual(self.site_id, '1')
        self.assertFalse(self.site_id == '1')
        self.assertTrue(self.site_id < '1')
        self.assertTrue(self.site_id <= '1')
        self.assertFalse(self.site_id > '1')
        self.assertFalse(self.site_id >= '1')
        # int <op> SiteIDHook
        self.assertNotEqual('1', self.site_id)
        self.assertFalse('1' == self.site_id)
        self.assertFalse('1' < self.site_id)
        self.assertFalse('1' <= self.site_id)
        self.assertTrue('1' > self.site_id)
        self.assertTrue('1' >= self.site_id)

    def test_set(self):
        self.site_id.set(10)
        self.assertEqual(int(self.site_id), 10)
        self.site_id.set(20)
        self.assertEqual(int(self.site_id), 20)
        self.site_id.set(self.site)
        self.assertEqual(int(self.site_id), self.site.id)

    def test_hash(self):
        self.site_id.set(10)
        self.assertEqual(hash(self.site_id), 10)
        self.site_id.set(20)
        self.assertEqual(hash(self.site_id), 20)
