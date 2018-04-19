from __future__ import unicode_literals
from __future__ import absolute_import

from django.utils.functional import empty, SimpleLazyObject


__ALL__ = ('ALLOWED_HOSTS', 'AllowedHosts')

_wrapped_default = empty


class IterableLazyObject(SimpleLazyObject):

    _wrapped_default = globals()['_wrapped_default']

    def __iter__(self):
        if self._wrapped is self._wrapped_default:
            self._setup()
        return self._wrapped.__iter__()


class AllowedHosts(object):

    alias_model = None

    def __init__(self):
        from django.conf import settings
        self.extra_hosts = getattr(settings, 'MULTISITE_EXTRA_HOSTS', [])

        if self.alias_model is None:
            from .models import Alias
            self.alias_model = Alias

    def __iter__(self):
        # Yielding extra hosts before actual hosts because there might be
        # wild cards in there that would prevent us from doing a database
        # query every time.
        for host in self.extra_hosts:
            yield host

        for host in self.alias_model.objects.values_list('domain'):
            yield host[0]

ALLOWED_HOSTS = IterableLazyObject(lambda: AllowedHosts())
