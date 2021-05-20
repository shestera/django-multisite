# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loaders.filesystem import Loader as FilesystemLoader


class Loader(FilesystemLoader):
    def get_template_sources(self, *args, **kwargs):
        template_name = args[0]
        domain = Site.objects.get_current().domain
        default_dir = getattr(
            settings, 'MULTISITE_DEFAULT_TEMPLATE_DIR', 'default'
        )
        for tname in (os.path.join(domain, template_name),
                      os.path.join(default_dir, template_name)):
            args = [tname]
            for item in super(Loader, self).get_template_sources(*args, **kwargs):
                yield item
