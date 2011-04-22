from django.contrib import admin

class MultisiteModelAdmin(admin.ModelAdmin):
    """
    A very helpful modeladmin class for handling multi-site django applications.
    """
    def queryset(self, request):
        """
        Filters lists of items to items belonging to sites assigned to the
        current member.

        Additionally, for cases where the field containing a reference to 'site'
        or 'sites' isn't immediate-- one can supply the ModelAdmin class with
        a list of fields to check the site of:

         - multisite_filter_fields
            A list of paths to a 'site' or 'sites' field on a related model to
            filter the queryset on.

        (As long as you're not a superuser)
        """
        qs = super(MultisiteModelAdmin, self).queryset(request)
        if(request.user.is_superuser):
            return qs
        user_sites = request.user.get_profile().sites.all()
        if(hasattr(qs.model, "site")):
            qs = qs.filter(
                    site__in = user_sites
                )
        elif(hasattr(qs.model, "sites")):
            qs = qs.filter(
                    sites__in = user_sites
                )
        if(hasattr(self, "multisite_filter_fields")):
            for field in self.multisite_filter_fields:
                qkwargs = {
                        "{field}__in".format(field = field): user_sites
                        }
                qs = qs.filter(**qkwargs)
        return qs

    def handle_multisite_foreign_keys(self, db_field, request, **kwargs):
        """ 
        Filters the foreignkey queryset for fields referencing other models 
        to those models assigned to a site belonging to the current member.

        Also prevents users from assigning objects to sites that they are not
        members of.

        (As long as you're not a superuser)
        """
        if(not request.user.is_superuser):
            user_sites = request.user.get_profile().sites.all()
            if(hasattr(db_field.rel.to, "site")):
                kwargs["queryset"] = db_field.rel.to.objects.filter(
                            site__in = user_sites
                        )
            if(hasattr(db_field.rel.to, "sites")):
                kwargs["queryset"] = db_field.rel.to.objects.filter(
                            sites__in = user_sites
                        )
            if db_field.name == "site" or db_field.name == "sites":
                kwargs["queryset"] = user_sites
        return kwargs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs  = self.handle_multisite_foreign_keys(db_field, request, **kwargs)
        return super(MultisiteModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs = self.handle_multisite_foreign_keys(db_field, request, **kwargs)
        return super(MultisiteModelAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
