from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import logging
import os
import tempfile

from django.conf import settings
from django.core.management.base import BaseCommand

import tldextract


class Command(BaseCommand):
    def handle(self, **options):
        self.setup_logging(verbosity=options.get('verbosity', 1))

        filename = getattr(
            settings, 'MULTISITE_PUBLIC_SUFFIX_LIST_CACHE',
            os.path.join(tempfile.gettempdir(), 'multisite_tld.dat')
        )
        self.log("Updating {filename}".format(filename=filename))

        extract = tldextract.TLDExtract(cache_file=filename)
        extract.update(fetch_now=True)
        self.log("Done.")

    def setup_logging(self, verbosity):
        self.verbosity = int(verbosity)

        # Connect to tldextract's logger
        self.logger = logging.getLogger('tldextract')
        if self.verbosity < 2:
            self.logger.setLevel(logging.CRITICAL)

    def log(self, msg):
        self.logger.info(msg)
