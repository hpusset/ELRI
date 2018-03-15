from django.db import models
from django.contrib import messages
from metashare.repository.models import resourceInfoType_model
from metashare.repository.supermodel import _make_choices_from_list

DELIVERABLES = _make_choices_from_list(
    ["CEF-ELRC", "ELRC+ LOT2", "LOT3 D2.1", "LOT3 D2.2", "LOT3 D2.3", "LOT3 D2.4", "LOT3 D3.1", "LOT3 D3.2", "LOT3 D3.3", ])


class ManagementObject(models.Model):
    resource = models.OneToOneField(resourceInfoType_model, blank=True, null=True, related_name="management_object")

    delivered = models.CharField(
        verbose_name='Delivered',
        choices=sorted(DELIVERABLES['choices']),
        max_length=10, blank=True, null=True)

    to_be_delivered = models.CharField(
        verbose_name='To be delivered',
        choices=sorted(DELIVERABLES['choices']),
        max_length=10, blank=True, null=True)

    rejected = models.BooleanField(verbose_name="Rejected", default=False)

    rejection_reason = models.TextField(max_length=1000, blank=True, null=True)

    unique_together = ("rejected", "rejection_reason")

    def __unicode__(self):
        _unicode = u'{} (id: "{}")'.format(self.resource, self.id)
        return _unicode

    def save(self, *args, **kwargs):
        if not self.resource:
            self.resource = self.get_related_resource().__unicode__()
        if self.rejected and not self.rejection_reason:
            return
        elif not self.rejected and self.rejection_reason:
            self.rejection_reason = None
        super(ManagementObject, self).save(*args, **kwargs)
