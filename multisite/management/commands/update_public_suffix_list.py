import logging
import os
import tempfile

from django.conf import settings
from django.core.management.base import NoArgsCommand

import tldextract


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        self.setup_logging(verbosity=options.get('verbosity', 1))

        filename = getattr(
            settings, 'MULTISITE_PUBLIC_SUFFIX_LIST_CACHE',
            os.path.join(tempfile.gettempdir(), 'multisite_tld.dat')
        )
        self.log("Updating {filename}".format(filename=filename))

        with tempfile.NamedTemporaryFile(dir=os.path.dirname(filename)) as f:
            tmpname = f.name

            extract = tldextract.TLDExtract(fetch=True, cache_file=tmpname)
            extract._get_tld_extractor()
            self.log(
                "Downloaded new data to {filename}".format(filename=tmpname)
            )
            os.rename(tmpname, filename)
            f.delete = False    # No need to delete f any more.

        self.log("Done.")

    def setup_logging(self, verbosity):
        self.verbosity = int(verbosity)

        # Mute tldextract's logger
        logger = logging.getLogger('tldextract')
        if self.verbosity < 2:
            logger.setLevel(logging.CRITICAL)

    def log(self, msg, level=2):
        if self.verbosity >= level:
            print msg
