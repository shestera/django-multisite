# -*- coding: utf-8 -*

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


_thread_locals = local()


def get_request():
    return getattr(_thread_locals, 'request', None)


class ThreadLocalsMiddleware(object):
    """Middleware that saves request in thread local starage"""
    def process_request(self, request):
        _thread_locals.request = request


class SiteIDHook(local):
    def __init__(self):
        self.reset()

    def __repr__(self):
        return str(self.__int__())

    def __int__(self):
        if self.site_id is None:
            return 1
        return self.site_id

    def __lt__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() < other
        elif isinstance(other, SiteIDHook):
            return self.__int__() < other.__int__()
        return True

    def __le__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() <= other
        elif isinstance(other, SiteIDHook):
            return self.__int__() <= other.__int__()
        return True

    def __eq__(self, other):
        if isinstance(other, (int, long)):
            return self.__int__() == other
        elif isinstance(other, SiteIDHook):
            return self.__int__() == other.__int__()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __hash__(self):
        return self.__int__()

    def set(self, value):
        from django.db.models import Model
        if isinstance(value, Model):
            value = value.pk
        self.site_id = value

    def reset(self):
        self.site_id = None
