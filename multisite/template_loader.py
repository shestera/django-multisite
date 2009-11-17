from django.template import TemplateDoesNotExist
from django.utils._os import safe_join
import os.path
from django.contrib.sites.models import Site
from django.conf import settings

def get_template_sources(template_name, template_dirs=None):
    template_dir = os.path.join(settings.TEMPLATE_DIRS[0], Site.objects.get_current().domain)
    try:
        yield safe_join(template_dir, template_name)
    except UnicodeDecodeError:
        raise
    except ValueError:
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
