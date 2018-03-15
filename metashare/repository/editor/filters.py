from django.contrib.admin import SimpleListFilter


class ValidatedFilter(SimpleListFilter):
    title = 'Validated'
    parameter_name = "validated"

    def lookups(self, request, model_admin):
        """
            List of values to allow admin to select
        """
        return (
            ('YES', 'YES'),
            ('NO', 'NO'),
        )

    def queryset(self, request, queryset):
        result = list()
        if self.value() == 'YES':
            for obj in queryset:
                if obj.storage_object.get_validation():
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        elif self.value() == 'NO':
            for obj in queryset:
                if not obj.storage_object.get_validation():
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        else:
            return queryset


class ResourceTypeFilter(SimpleListFilter):
    title = 'Resource Type'
    parameter_name = "resource_type"

    def lookups(self, request, model_admin):
        """
            List of values to allow admin to select
        """
        return (
            ('Corpus', 'Corpus'),
            ('Lexical conceptual resource', 'Lexical conceptual resource'),
            ('Language description', 'Language description'),
            ('Tool service', 'Tool service')
        )

    @staticmethod
    def _get_resource_type(obj):
        return obj.resource_type()

    def queryset(self, request, queryset):
        result = list()
        if self.value() == 'Corpus':
            for obj in queryset:
                if self._get_resource_type(obj) == 'Corpus':
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        elif self.value() == 'Lexical conceptual resource':
            for obj in queryset:
                if self._get_resource_type(obj) == 'Lexical conceptual resource':
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        elif self.value() == 'Language description':
            for obj in queryset:
                if self._get_resource_type(obj) == 'Language description':
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        elif self.value() == 'Tool service':
            for obj in queryset:
                if self._get_resource_type(obj) == 'Tool service':
                    result.append(obj.id)
            return queryset.filter(id__in=result)
        else:
            return queryset
