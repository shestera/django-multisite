from django.template import TemplateDoesNotExist
from django.utils._os import safe_join
import os.path
from django.contrib.sites.models import Site
from django.conf import settings
from django.template.loaders.app_directories import *


def get_template_sources(template_name, template_dirs=None):
    template_dir = os.path.join(settings.TEMPLATE_DIRS[0], Site.objects.get_current().domain)
    if not template_dirs:
        template_dirs = app_template_dirs
        for template_dir in template_dirs:
            try:
                template_dir = os.path.join(template_dir, Site.objects.get_current().domain)
                yield safe_join(template_dir, template_name)
            except UnicodeDecodeError:
                # The template dir name was a bytestring that wasn't valid UTF-8.
                raise
            except ValueError:
                # The joined path was located outside of template_dir.
                pass
                

def load_template_source(template_name, template_dirs=None):
    tried = []
    for filepath in get_template_sources(template_name, template_dirs):
        try:
            return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
        except IOError:
            tried.append(filepath)
    if tried:
        error_msg = "Tried %s" % tried
    else:
        error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
    raise TemplateDoesNotExist, error_msg
load_template_source.is_usable = True
