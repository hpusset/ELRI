from django import forms
from project_management.models import ManagementObject, DELIVERABLES


class ManagementObjectForm(forms.ModelForm):
    class Meta:
        model = ManagementObject
        fields = ['delivered', 'to_be_delivered', 'rejected', 'rejection_reason']


class IntermediateDeliverableSelectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    deliverable = forms.ChoiceField(choices=DELIVERABLES['choices'], required=True)


class IntermediateDeliverableRejectForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    rejection_reason = forms.CharField(widget=forms.Textarea, required=True )
