from distutils.core import setup
import os

_dir_ = os.path.dirname(__file__)


def long_description():
    """Returns the value of README.rst"""
    with open(os.path.join(_dir_, 'README.rst')) as f:
        return f.read()


setup(name='django-multisite',
      version='0.2.3',
      description='Serve multiple sites from a single Django application',
      long_description=long_description(),
      author='Leonid S Shestera',
      author_email='leonid@shestera.ru',
      maintainer='Ecometrica',
      maintainer_email='info@ecometrica.com',
      url='http://github.com/ecometrica/django-multisite',
      packages=['multisite',
                'multisite.migrations'],
      install_requires=['Django>=1.3'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Internet',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'],
)
