from django.contrib.admin import SimpleListFilter


class PublicationStatusFilter(SimpleListFilter):
    title = 'Publication Status'
    parameter_name = "publication_status"

    def lookups(self, request, model_admin):
        """
            List of values to allow admin to select
        """
        return (
            ('internal', 'internal'),
            ('ingested', 'ingested'),
            ('published', 'published')
        )

    def queryset(self, request, queryset):
        if self.value() == 'internal':
            return queryset.filter(resource__storage_object__publication_status='i')
        elif self.value() == 'ingested':
            return queryset.filter(resource__storage_object__publication_status='g')
        elif self.value() == 'published':
            return queryset.filter(resource__storage_object__publication_status='p')
        else:
            return queryset