from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django_password_validation import validate_password

from metashare.accounts.models import UserProfile, EditorGroupApplication, \
    OrganizationApplication, Organization, OrganizationManagers, EditorGroup, \
    EditorGroupManagers, AccessPointEdeliveryApplication
from metashare.accounts.validators import validate_wsdl_url
from metashare.settings import LOG_HANDLER
import logging
## Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)


class ModelForm(forms.ModelForm):
    """
    Base form for META-SHARE model forms -- disables the colon after a label,
    and formats error messages as expected by the templates.
    """

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # Avoid the default ':' suffix
        self.label_suffix = ''

    required_css_class = 'required'
    error_css_class = 'error'

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row=u'<tr%(html_class_attr)s><th>%(label)s%(errors)s</th><td>%(field)s%(help_text)s</td></tr>',
            error_row=u'<tr><td colspan="2">%s</td></tr>',
            row_ender=u'</td></tr>',
            help_text_html=u'<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)


class Form(forms.Form):
    """
    Base form for META-SHARE forms -- disables the colon after a label,
    and formats error messages as expected by the templates.
    """

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        # Avoid the default ':' suffix
        self.label_suffix = ''

    required_css_class = 'required'
    error_css_class = 'error'

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row=u'<tr%(html_class_attr)s><th>%(label)s%(errors)s</th><td>%(field)s%(help_text)s</td></tr>',
            error_row=u'<tr><td colspan="2">%s</td></tr>',
            row_ender=u'</td></tr>',
            help_text_html=u'<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)


class RegistrationRequestForm(Form):
    """
    Form used to create user account requests from new users.
    """
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z@.+\-_]*$', _(u'This value may contain only letters, numbers and @/./+/-/_ characters.'))
    shortname = forms.CharField(max_length=User._meta.get_field('username').max_length,validators=[alphanumeric],
                                label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Desired account name")))
    first_name = forms.CharField(User._meta.get_field('first_name').max_length,
                                 label=mark_safe(u"%s<span style='color:red'>*</span>" % _("First name")))
    last_name = forms.CharField(User._meta.get_field('last_name').max_length,
                                label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Last name")))
    email = forms.EmailField(label=mark_safe(u"%s<span style='color:red'>*</span>" % _("E-mail")))

	# For National Relay Stations, the country is limited to the Member State in which the NRS is deployed
    #country = forms.ChoiceField(UserProfile._meta.get_field('country').choices,
                                #UserProfile._meta.get_field('country').max_length,
                                #label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Country")))

    organization = forms.CharField(UserProfile._meta.get_field('affiliation').max_length,
                                   label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Organization name")))
    organization_address = forms.CharField(
            UserProfile._meta.get_field('affiliation_address').max_length,
            label=mark_safe(u"%s<span style='color:red'>*</span>"
                            % _("Organization address")))
    organization_phone_number = forms.CharField(
            UserProfile._meta.get_field('affiliation_phone_number').max_length,
            label=mark_safe( _("Organization phone number")),required=False)
    position = forms.CharField(UserProfile._meta.get_field('position').max_length,
                               label=mark_safe(_("Position in the organization")),required=False)


    #Removing user phone number for now: user email and organisation phone number should be sufficient
    #phone_number = forms.CharField(UserProfile._meta.get_field('phone_number').max_length,
                                   #label=mark_safe(u"%s<span style='color:grey'>*</span>" % _("Phone number")))

    password = forms.CharField(User._meta.get_field('password').max_length,
                               label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Password")),
                               widget=forms.PasswordInput())
    confirm_password = forms.CharField(
        User._meta.get_field('password').max_length,
        label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Password confirmation")), widget=forms.PasswordInput())


	#Commenting from now, as it might be more functional to handle group assignment for logged in users
	## In ELRI we need users to be able to join more than one group
    #contributor_group = forms.MultipleChoiceField(
        #label=mark_safe(u"%s<span style='color:red'>*</span>" % _("Contributor group"))
        #)

    accepted_tos = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        group_choices = kwargs.pop("group_choices")
        super(RegistrationRequestForm, self).__init__(*args, **kwargs)
        #self.fields["contributor_group"].choices = group_choices

    def clean_shortname(self):
        """
        Make sure that the user name is still available.
        """
        _user_name = self.cleaned_data['shortname']

        try:
            User.objects.get(username=_user_name)
        except:
            pass
        else:
            raise ValidationError(_('User account name already exists, ' \
                                    'please choose another one.'))
        return _user_name

    def clean_email(self):
        """
        Make sure that there is no account yet registered with this email.
        """
        _email = self.cleaned_data['email']
        try:
            User.objects.get(email=_email)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            raise ValidationError(_('There is already an account registered ' \
                                    'with this e-mail address.'))
        else:
            raise ValidationError(_('There is already an account registered ' \
                                    'with this e-mail address.'))
        return _email

    def clean_confirm_password(self):
        """
        Make sure that the password confirmation is the same as password.
        """
        pswrd = self.cleaned_data.get('password', None)
        pswrd_conf = self.cleaned_data['confirm_password']
        if pswrd != pswrd_conf:
            raise ValidationError(_('The two password fields did not match.'))
        if 'shortname' in self.cleaned_data.keys(): #check password iif there is a valid username, to avoid 
            validate_password(pswrd, user=User(
                # this in-memory object is just for password validation
                username=self.cleaned_data['shortname'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            ))
            validate_password(pswrd, user=UserProfile(
                # this in-memory object is just for password validation
                user_id=1, # dummy foreign key

                affiliation=self.cleaned_data['organization'],
                affiliation_address=self.cleaned_data['organization_address'],
                affiliation_phone_number=self.cleaned_data['organization_phone_number'],
            ))
        return pswrd

        # cfedermann: possible extensions for future improvements.
        # - add validation for shortname for forbidden characters


class EdeliveryApplicationForm(Form):
    # class Meta:
    #     """
    #     Meta class connecting to UserProfile object model.
    #     """
    #     model = AccessPointEdeliveryApplication
    #     exclude = ('user', 'status', 'created', 'rejection_reason')

    endpoint = forms.URLField(validators=[validate_wsdl_url], required=True)
    gateway_party_name = forms.CharField(max_length=100, required=True)
    gateway_party_id = forms.CharField(max_length=100, required=True)
    public_key = forms.FileField(required=True)


class ContactForm(Form):
    """
    Form used to contact the superusers of the META-SHARE node.
    """
    subject = forms.CharField(min_length=6, max_length=80,label=_(u'Subject'),
                              error_messages={'min_length': _('Please provide a meaningful and '
                                                              'sufficiently indicative subject.')})
    message = forms.CharField(min_length=30, max_length=2500,label=_(u'Message'),
                              widget=forms.Textarea, error_messages={'min_length': _('Your message '
                                                                                     'appears to be rather short. Please make sure to phrase your '
                                                                                     'request as precise as possible. This will help us to process it '
                                                                                     'as quick as possible.')})


class ResetRequestForm(Form):
    """
    Form used to reset an existing user account.
    """
    username = forms.CharField(max_length=30, label=_(u'Username'))
    email = forms.EmailField(label=_(u'Email'))

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if username and email:
            # Only do something if both fields are valid so far.
            user = User.objects.filter(username=username, email=email)
            if not user:
                raise forms.ValidationError(_('Not a valid username-email combination.'))

        return cleaned_data


class UserProfileForm(ModelForm):
    """
    Form used to update the user account profile information.
    """

    class Meta:
        """
        Meta class connecting to UserProfile object model.
        """
        model = UserProfile
        exclude = ('user', 'modified', 'uuid', 'default_editor_groups', 'country')


class EditorGroupApplicationForm(ModelForm):
    """
    Form used to apply to new editor groups membership.
    """

    class Meta:
        """
        Meta class connecting to EditorGroupApplication object model.
        """
        model = EditorGroupApplication
        exclude = ('user', 'created')

    def __init__(self, editor_group_qs, *args, **kwargs):
        """
        Initializes the `EditorGroupApplicationForm` with the editor groups
        of the given query set.
        """
        super(EditorGroupApplicationForm, self).__init__(*args, **kwargs)
        # If there is a list of editor groups, then modify the ModelChoiceField
        self.fields['editor_group'].queryset = editor_group_qs


class UpdateDefaultEditorGroupForm(ModelForm):
    """
    Form used to update default editor groups.
    """
    default_editor_groups = forms.ModelMultipleChoiceField([],
                                                           widget=widgets.FilteredSelectMultiple(
                                                               _("default editor groups"),
                                                               is_stacked=False),
                                                           required=False)

    class Media:
        css = {
            # required by the FilteredSelectMultiple widget
            'all': ['{}admin/css/widgets.css'.format(settings.STATIC_URL)],
        }
        # required by the FilteredSelectMultiple widget
        js = ['/{}admin/jsi18n/'.format(settings.DJANGO_BASE)]

    class Meta:
        """
        Meta class connecting to UserProfile object model.
        """
        model = UserProfile
        exclude = ('user', 'modified', 'uuid', 'birthdate', 'affiliation', \
                   'position', 'homepage')

    def __init__(self, available_editor_group, chosen_editor_group, *args, **kwargs):
        """
        Initializes the `UpdateDefaultEditorGroupForm` with the editor groups
        of the given query set.
        """
        super(UpdateDefaultEditorGroupForm, self).__init__(*args, **kwargs)
        # If there is a list of editor groups, then modify the ModelChoiceField
        self.fields['default_editor_groups'].queryset = available_editor_group
        self.fields['default_editor_groups'].initial = chosen_editor_group


class OrganizationApplicationForm(ModelForm):
    """
    Form used to apply to new organizations membership.
    """

    class Meta:
        """
        Meta class connecting to OrganizationApplication object model.
        """
        model = OrganizationApplication
        exclude = ('user', 'created')

    def __init__(self, organization_qs, *args, **kwargs):
        """
        Initializes the `OrganizationApplicationForm` with the organizations
        of the given query set.
        """
        super(OrganizationApplicationForm, self).__init__(*args, **kwargs)
        # If there is a list of organizations, then modify the ModelChoiceField
        self.fields['organization'].queryset = organization_qs


class EditorGroupForm(ModelForm):
    """
    Form used to render the add/change admin views for `EditorGroup` model
    instances.
    """

    class Meta:
        model = EditorGroup
        exclude = ()
        widgets = {
            'permissions': forms.widgets.MultipleHiddenInput
        }


class EditorGroupManagersForm(ModelForm):
    """
    Form used to render the add/change admin views for `EditorGroupManagers`
    model instances.
    """

    class Meta:
        model = EditorGroupManagers
        exclude = ()
        widgets = {
            'permissions': forms.widgets.MultipleHiddenInput
        }


class OrganizationForm(ModelForm):
    """
    Form used to render the add/change admin views for `Organization` model
    instances.
    """

    class Meta:
        model = Organization
        exclude = ()
        widgets = {
            'permissions': widgets.FilteredSelectMultiple(
                Organization._meta.get_field('permissions').verbose_name, False)
        }


class OrganizationManagersForm(ModelForm):
    """
    Form used to render the add/change admin views for `OrganizationManagers`
    model instances.
    """

    class Meta:
        model = OrganizationManagers
        exclude = ()
        widgets = {
            'permissions': widgets.FilteredSelectMultiple(OrganizationManagers \
                                                          ._meta.get_field('permissions').verbose_name, False)
        }
