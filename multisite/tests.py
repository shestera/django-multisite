import warnings

from django.conf import settings
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import RequestFactory as DjangoRequestFactory
from django.utils.unittest import skipUnless

try:
    from django.test.utils import override_settings
except ImportError:
    from override_settings import override_settings

from . import SiteID, threadlocals
from .middleware import DynamicSiteMiddleware, HOST_CACHE
from .threadlocals import SiteIDHook


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
@override_settings(SITE_ID=SiteID())
class TestContribSite(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain='example.com')
        settings.SITE_ID.set(self.site.id)

    def test_get_current_site(self):
        current_site = Site.objects.get_current()
        self.assertEqual(current_site, self.site)
        self.assertEqual(current_site.id, settings.SITE_ID)


@skipUnless(Site._meta.installed,
            'django.contrib.sites is not in settings.INSTALLED_APPS')
@override_settings(SITE_ID=SiteID(default=1))
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
        settings.SITE_ID.reset()

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


class TestSiteID(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain='example.com')
        self.site_id = SiteID()

    def test_invalid_default(self):
        self.assertRaises(ValueError, SiteID, default='a')
        self.assertRaises(ValueError, SiteID, default=self.site_id)

    def test_compare_default_site_id(self):
        self.site_id = SiteID(default=self.site.id)
        self.assertEqual(self.site_id, self.site.id)
        self.assertFalse(self.site_id != self.site.id)
        self.assertFalse(self.site_id < self.site.id)
        self.assertTrue(self.site_id <= self.site.id)
        self.assertFalse(self.site_id > self.site.id)
        self.assertTrue(self.site_id >= self.site.id)

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

    def test_str_repr(self):
        self.site_id.set(10)
        self.assertEqual(str(self.site_id), '10')
        self.assertEqual(repr(self.site_id), '10')


class TestSiteIDHook(TestCase):
    def test_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            threadlocals.__warningregistry__ = {}
            SiteIDHook()
            self.assertTrue(w)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

    def test_default_value(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            site_id = SiteIDHook()
            self.assertEqual(site_id.default, 1)
            self.assertEqual(int(site_id), 1)
