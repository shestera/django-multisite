from django.conf import settings
from django.contrib.sites import checks
from django.core.checks import Error

from . import SiteID


def check_site_id(app_configs, **kwargs):
    """ Patch sites check because django 3.2 insists on an integer value for SITE_ID """
    if (
        hasattr(settings, 'SITE_ID') and
        not isinstance(settings.SITE_ID, (type(None), int, SiteID))
    ):
        return [
            Error('The SITE_ID setting must be an integer or SiteID', id='sites.E101'),
        ]
    return []


checks.check_site_id = check_site_id
