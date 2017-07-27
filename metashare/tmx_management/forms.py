from django import forms


class TmxQueryForm(forms.Form):
    """
    A `Form` for sending a contact request regarding the download of a resource
    """
    lang1 = forms.Select(choices=(('en', 'English'), ('fr', 'French')))
