from django.contrib.admin import SimpleListFilter
from .models import DELIVERABLES


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


class DeliveredFilter(SimpleListFilter):
    title = 'Delivered'
    parameter_name = "delivered"

    def lookups(self, request, model_admin):
        """
            List of values to allow admin to select
        """
        delivs = [d for d in DELIVERABLES['choices']]
        delivs.append(('None', 'None'))
        return tuple(delivs)

    def queryset(self, request, queryset):
        if self.value() == 'CEF-ELRC':
            return queryset.filter(delivered='CEF-ELRC')
        elif self.value() == 'ELRC Network':
            return queryset.filter(delivered='ELRC Network')
        elif self.value() == 'ELRC Data D2.1':
            return queryset.filter(delivered='ELRC Data D2.1')
        elif self.value() == 'ELRC Data D2.2':
            return queryset.filter(delivered='ELRC Data D2.2')
        elif self.value() == 'ELRC Data D2.3':
            return queryset.filter(delivered='ELRC Data D2.3')
        elif self.value() == 'ELRC Data D2.4':
            return queryset.filter(delivered='ELRC Data D2.4')
        elif self.value() == 'ELRC Data D3.1':
            return queryset.filter(delivered='ELRC Data D3.1')
        elif self.value() == 'ELRC Data D3.2':
            return queryset.filter(delivered='ELRC Data D3.2')
        elif self.value() == 'ELRC Data D3.3':
            return queryset.filter(delivered='ELRC Data D3.3')
        elif self.value() == "None":
            return queryset.filter(delivered=None)
        else:
            return queryset


class ToBeDeliveredFilter(SimpleListFilter):
    title = 'To be Delivered'
    parameter_name = "to_be_delivered"

    def lookups(self, request, model_admin):
        """
            List of values to allow admin to select
        """
        delivs = [d for d in DELIVERABLES['choices']]
        delivs.append(('None', 'None'))
        return tuple(delivs)

    def queryset(self, request, queryset):
        if self.value() == 'CEF-ELRC':
            return queryset.filter(delivered='CEF-ELRC')
        elif self.value() == 'ELRC Network':
            return queryset.filter(delivered='ELRC Network')
        elif self.value() == 'ELRC Data D2.1':
            return queryset.filter(delivered='ELRC Data D2.1')
        elif self.value() == 'ELRC Data D2.2':
            return queryset.filter(delivered='ELRC Data D2.2')
        elif self.value() == 'ELRC Data D2.3':
            return queryset.filter(delivered='ELRC Data D2.3')
        elif self.value() == 'ELRC Data D2.4':
            return queryset.filter(delivered='ELRC Data D2.4')
        elif self.value() == 'ELRC Data D3.1':
            return queryset.filter(delivered='ELRC Data D3.1')
        elif self.value() == 'ELRC Data D3.2':
            return queryset.filter(delivered='ELRC Data D3.2')
        elif self.value() == 'ELRC Data D3.3':
            return queryset.filter(delivered='ELRC Data D3.3')
        elif self.value() == "None":
            return queryset.filter(delivered=None)
        else:
            return queryset
