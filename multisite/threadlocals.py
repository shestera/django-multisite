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


class SiteIDHook(object):
    def __repr__(self):
        return str(self.__int__())

    def __int__(self):
        try:
            return _thread_locals.SITE_ID
        except AttributeError:
            _thread_locals.SITE_ID = 1
            return _thread_locals.SITE_ID

    def __hash__(self):
        return self.__int__()

    def set(self, value):
        _thread_locals.SITE_ID = value
