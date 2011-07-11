from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site


class PathAssistedCurrentSiteManager(CurrentSiteManager):
    def __init__(self, field_path):
        super(PathAssistedCurrentSiteManager, self).__init__()
        self.__field_path = field_path

    def get_query_set(self):
        return super(CurrentSiteManager, self).get_query_set().filter(
                    **{self.__field_path: Site.objects.get_current()}
                )
