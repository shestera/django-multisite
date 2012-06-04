from distutils.core import setup
import os

_dir_ = os.path.dirname(__file__)


def long_description():
    """Returns the value of README.rst"""
    with open(os.path.join(_dir_, 'README.rst')) as f:
        return f.read()


setup(name='django-multisite',
      version='0.1',
      description='Multisite for Django',
      long_description=long_description(),
      author='Leonid S Shestera',
      author_email='leonid@shestera.ru',
      url='http://github.com/shestera/django-multisite',
      packages=['multisite',
                'multisite.migrations'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
