from distutils.core import setup


setup(name='django-multisite',
      version='0.1',
      description='Multisite for Django',
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
