from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import connections, models, router
from django.db.models.signals import pre_save, post_save, post_syncdb
from django.utils.translation import ugettext_lazy as _


_site_domain = Site._meta.get_field('domain')


class AliasManager(models.Manager):
    """Manager for all Aliases."""

    def get_query_set(self):
        return super(AliasManager, self).get_query_set().select_related('site')


class CanonicalAliasManager(models.Manager):
    """Manager for Alias objects where is_canonical is True."""

    def get_query_set(self):
        qset = super(CanonicalAliasManager, self).get_query_set()
        return qset.filter(is_canonical=True)

    def sync_many(self, *args, **kwargs):
        """
        Synchronize canonical Alias objects based on Site.domain.

        You can pass Q-objects or filter arguments to update a subset of
        Alias objects::

            Alias.canonical.sync_many(site__domain='example.com')
        """
        aliases = self.get_query_set().filter(*args, **kwargs)
        for alias in aliases.select_related('site'):
            domain = alias.site.domain
            if domain and alias.domain != domain:
                alias.domain = domain
                alias.save()

    def sync_missing(self):
        """Create missing canonical Alias objects based on Site.domain."""
        aliases = self.get_query_set()
        sites = self.model._meta.get_field('site').rel.to
        for site in sites.objects.exclude(aliases__in=aliases):
            Alias.sync(site=site)

    def sync_all(self):
        """Create or sync canonical Alias objects from all Site objects."""
        self.sync_many()
        self.sync_missing()


class NotCanonicalAliasManager(models.Manager):
    """Manager for Aliases where is_canonical is None."""

    def get_query_set(self):
        qset = super(NotCanonicalAliasManager, self).get_query_set()
        return qset.filter(is_canonical__isnull=True)


def validate_true_or_none(value):
    """Raises ValidationError if value is not True or None."""
    if value not in (True, None):
        raise ValidationError(u'%r must be True or None' % value)


class Alias(models.Model):
    """
    Model for domain-name aliases for Site objects.

    Domain names must be unique in the format of: 'hostname[:port].'
    Each Site object that has a domain must have an ``is_canonical``
    Alias.
    """

    site = models.ForeignKey(Site, related_name='aliases')
    domain = type(_site_domain)(_('domain name'),
                                max_length=_site_domain.max_length,
                                unique=True)
    is_canonical = models.NullBooleanField(default=None, editable=False,
                                           validators=[validate_true_or_none])

    objects = AliasManager()
    canonical = CanonicalAliasManager()
    aliases = NotCanonicalAliasManager()

    class Meta:
        unique_together = [('is_canonical', 'site')]
        verbose_name_plural = _('aliases')

    def __unicode__(self):
        return "%s -> %s" % (self.domain, self.site.domain)

    def save_base(self, *args, **kwargs):
        self.full_clean()
        super(Alias, self).save_base(*args, **kwargs)

    def clean_fields(self, exclude=None, *args, **kwargs):
        errors = {}
        try:
            super(Alias, self).clean_fields(exclude=exclude, *args, **kwargs)
        except ValidationError, e:
            errors = e.update_error_dict(errors)

        try:
            self.clean_domain()
        except ValidationError, e:
            errors = e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    def clean_domain(self):
        # For canonical Alias, domains must match Site domains.
        if self.is_canonical and self.domain != self.site.domain:
            raise ValidationError(
                {'domain': ['Does not match %r' % self.site]}
            )

    def validate_unique(self, exclude=None):
        errors = {}
        try:
            super(Alias, self).validate_unique(exclude=exclude)
        except ValidationError, e:
            errors = e.update_error_dict(errors)

        if exclude is not None and 'domain' not in exclude:
            # Ensure domain is unique, insensitive to case
            field_name = 'domain'
            field_error = self.unique_error_message(self.__class__,
                                                    (field_name,))
            if field_name not in errors or \
               field_error not in errors[field_name]:
                qset = self.__class__.objects.filter(
                    **{field_name + '__iexact': getattr(self, field_name)}
                )
                if self.pk is not None:
                    qset = qset.exclude(pk=self.pk)
                if qset.exists():
                    errors.setdefault(field_name, []).append(field_error)

        if errors:
            raise ValidationError(errors)

    @classmethod
    def _sync_blank_domain(cls, site):
        """Delete associated Alias object for ``site``, if domain is blank."""

        if site.domain:
            raise ValueError('%r has a domain' % site)

        # Remove canonical Alias, if no non-canonical aliases exist.
        try:
            alias = cls.objects.get(site=site)
        except cls.DoesNotExist:
            # Nothing to delete
            pass
        else:
            if not alias.is_canonical:
                raise cls.MultipleObjectsReturned(
                    'Other %s still exist for %r' %
                    (cls._meta.verbose_name_plural.capitalize(), site)
                )
            alias.delete()

    @classmethod
    def sync(cls, site, force_insert=False):
        """
        Create or synchronize Alias object from ``site``.

        If `force_insert`, forces creation of Alias object.
        """
        domain = site.domain
        if not domain:
            cls._sync_blank_domain(site)
            return

        if force_insert:
            alias = cls.objects.create(site=site, is_canonical=True,
                                       domain=domain)

        else:
            alias, created = cls.objects.get_or_create(
                site=site, is_canonical=True,
                defaults={'domain': domain}
            )
            if not created and alias.domain != domain:
                alias.site = site
                alias.domain = domain
                alias.save()

        return alias

    @classmethod
    def site_domain_changed_hook(cls, sender, instance, raw, *args, **kwargs):
        """Updates canonical Alias object if Site.domain has changed."""
        if raw or instance.pk is None:
            return

        try:
            original = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

        # Update Alias.domain to match site
        if original.domain != instance.domain:
            cls.sync(site=instance)

    @classmethod
    def site_created_hook(cls, sender, instance, raw, created,
                          *args, **kwargs):
        """Creates canonical Alias object for a new Site."""
        if raw or not created:
            return

        # When running create_default_site() because of post_syncdb,
        # don't try to sync before the db_table has been created.
        using = router.db_for_write(cls)
        tables = connections[using].introspection.table_names()
        if cls._meta.db_table not in tables:
            return

        # Update Alias.domain to match site
        cls.sync(site=instance)

    @classmethod
    def db_table_created_hook(cls, created_models, *args, **kwargs):
        """Syncs canonical Alias objects for all existing Site objects."""
        if cls in created_models:
            Alias.canonical.sync_all()


# Hooks to handle Site objects being created or changed
pre_save.connect(Alias.site_domain_changed_hook, sender=Site)
post_save.connect(Alias.site_created_hook, sender=Site)

# Hook to handle syncdb creating the Alias table
post_syncdb.connect(Alias.db_table_created_hook, sender=Alias.__module__)
