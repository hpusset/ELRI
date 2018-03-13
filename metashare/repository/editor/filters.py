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
