# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loaders.filesystem import Loader as FilesystemLoader
from django.utils._os import safe_join


class Loader(FilesystemLoader):
    def get_template_sources(self, template_name, template_dirs=None):
        if not template_dirs:
            template_dirs = settings.TEMPLATE_DIRS

        domain = Site.objects.get_current().domain
        default_dir = getattr(settings, 'MULTISITE_DEFAULT_TEMPLATE_DIR', 'default')

        new_template_dirs = []
        for template_dir in template_dirs:
            new_template_dirs.append(safe_join(template_dir, domain))
            if default_dir:
                new_template_dirs.append(safe_join(template_dir, default_dir))

        for template_dir in new_template_dirs:
            try:
                yield safe_join(template_dir, template_name)
            except UnicodeDecodeError:
                # The template dir name was a bytestring that wasn't valid UTF-8.
                raise
            except ValueError:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass
