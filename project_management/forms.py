from django import forms
from project_management.models import ManagementObject, DELIVERABLES, IPR_CLEARING


class ManagementObjectForm(forms.ModelForm):
    class Meta:
        model = ManagementObject
        fields = ['delivered_to_EC', 'to_be_delivered_to_EC', 'rejected', 'rejection_reason']


class IntermediateDeliverableSelectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    deliverable = forms.ChoiceField(choices=DELIVERABLES['choices'], required=True)


class IntermediateDeliverableRejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    rejection_reason = forms.CharField(widget=forms.Textarea, required=True)


_choices = list(IPR_CLEARING['choices'])
_choices.insert(0, (None, "-------"))


class IntermediateIPRSelectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    ipr_status = forms.ChoiceField(choices=tuple(_choices),
                                   required=False)
