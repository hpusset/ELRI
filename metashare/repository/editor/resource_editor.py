import datetime, requests, os, zipfile
from functools import update_wrapper
from mimetypes import guess_type
from shutil import copyfile
import logging
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode, force_text
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ungettext
from django.views.decorators.csrf import csrf_protect



from metashare import settings
from metashare.settings import STATIC_URL,LOG_HANDLER,ROOT_PATH

from metashare.accounts.models import EditorGroup, EditorGroupManagers
from metashare.repository.editor.editorutils import FilteredChangeList, AllChangeList
from metashare.repository.editor.filters import ValidatedFilter, ResourceTypeFilter
from metashare.repository.editor.forms import StorageObjectUploadForm, ValidationUploadForm, LegalDocumetationUploadForm
from metashare.repository.editor.inlines import ReverseInlineFormSet, \
    ReverseInlineModelAdmin
from metashare.repository.editor.schemamodel_mixin import encode_as_inline
from metashare.repository.editor.superadmin import SchemaModelAdmin
from metashare.repository.editor.widgets import OneToManyWidget
from metashare.repository.models import resourceComponentTypeType_model, \
    corpusInfoType_model, languageDescriptionInfoType_model, \
    lexicalConceptualResourceInfoType_model, toolServiceInfoType_model, \
    corpusMediaTypeType_model, languageDescriptionMediaTypeType_model, \
    lexicalConceptualResourceMediaTypeType_model, resourceInfoType_model, \
    licenceInfoType_model, User
from metashare.repository.supermodel import SchemaModel
from metashare.stats.model_utils import saveLRStats, UPDATE_STAT, INGEST_STAT, DELETE_STAT
from metashare.storage.models import PUBLISHED, INGESTED, INTERNAL, \
    ALLOWED_ARCHIVE_EXTENSIONS, ALLOWED_VALIDATION_EXTENSIONS, ALLOWED_LEGAL_DOCUMENTATION_EXTENSIONS
from metashare.utils import verify_subclass, create_breadcrumb_template_params


from os.path import split, getsize

# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)


csrf_protect_m = method_decorator(csrf_protect)

# a type providing an enumeration of META-SHARE member types
MEMBER_TYPES = type('MemberEnum', (), dict(GOD=100, FULL=3, ASSOCIATE=2, NON=1))


# a dictionary holding a URL for each download licence and a member type which
# is required at a minimum to be able to download the associated resource
# straight away; otherwise the licence requires a hard-copy signature
LICENCEINFOTYPE_URLS_LICENCE_CHOICES = {
	'CC-BY-4.0': (STATIC_URL + 'metashare/licences/CC-BY-4.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-4.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-4.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-ND-4.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-ND-4.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-SA-4.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-SA-4.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-ND-4.0': (STATIC_URL + 'metashare/licences/CC-BY-ND-4.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-SA-4.0': (STATIC_URL + 'metashare/licences/CC-BY-SA-4.0.pdf', MEMBER_TYPES.NON),
	'CC0-1.0': (STATIC_URL + 'metashare/licences/CC0-1.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-3.0': (STATIC_URL + 'metashare/licences/CC-BY-3.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-3.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-3.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-ND-3.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-ND-3.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-NC-SA-3.0': (STATIC_URL + 'metashare/licences/CC-BY-NC-SA-3.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-ND-3.0': (STATIC_URL + 'metashare/licences/CC-BY-ND-3.0.pdf', MEMBER_TYPES.NON),
	'CC-BY-SA-3.0': (STATIC_URL + 'metashare/licences/CC-BY-SA-3.0.pdf', MEMBER_TYPES.NON),
	# TODO: PDDL
	'PDDL-1.0': (STATIC_URL + 'metashare/licences/PDDL-1.0.pdf', MEMBER_TYPES.NON),
	# TODO: ODC-BY
	'ODC-BY-1.0': (STATIC_URL + 'metashare/licences/ODC-BY-1.0.pdf', MEMBER_TYPES.NON),
	'ODbL-1.0': (STATIC_URL + 'metashare/licences/ODbL-1.0.pdf', MEMBER_TYPES.NON),
	'AGPL-3.0': (STATIC_URL + 'metashare/licences/AGPL-3.0.pdf', MEMBER_TYPES.NON),
	'Apache-2.0': (STATIC_URL + 'metashare/licences/Apache-2.0.pdf', MEMBER_TYPES.NON),
	'BSD-4-Clause': (STATIC_URL + 'metashare/licences/BSD-4-Clause.pdf', MEMBER_TYPES.NON),
	'BSD-3-Clause': (STATIC_URL + 'metashare/licences/BSD-3-Clause.pdf', MEMBER_TYPES.NON),
	'BSD-2-Clause': (STATIC_URL + 'metashare/licences/BSD-2-Clause', MEMBER_TYPES.NON),
	'GFDL-1.3': (STATIC_URL + 'metashare/licences/GFDL-1.3.pdf', MEMBER_TYPES.NON),
	'GPL-3.0': (STATIC_URL + 'metashare/licences/GPL-3.0.pdf', MEMBER_TYPES.NON),
	'LGPL-3.0': (STATIC_URL + 'metashare/licences/LGPL-3.0.pdf', MEMBER_TYPES.NON),
	'MIT': (STATIC_URL + 'metashare/licences/MIT.pdf', MEMBER_TYPES.NON),
	'EPL-1.0': (STATIC_URL + 'metashare/licences/EPL-1.0.pdf', MEMBER_TYPES.NON),
	'EUPL-1.0': (STATIC_URL + 'metashare/licences/EUPL-1.0.pdf', MEMBER_TYPES.NON),
	'EUPL-1.1': (STATIC_URL + 'metashare/licences/EUPL-1.1.pdf', MEMBER_TYPES.NON),
	'EUPL-1.2': (STATIC_URL + 'metashare/licences/EUPL-1.2.pdf', MEMBER_TYPES.NON),
	'LO-OL-v2': (STATIC_URL + 'metashare/licences/LO-OL-v2.pdf', MEMBER_TYPES.NON),
	'dl-de/by-2-0': (STATIC_URL + 'metashare/licences/dl-de_by-2-0.pdf', MEMBER_TYPES.NON),
	'dl-de/zero-2-0': (STATIC_URL + 'metashare/licences/dl-de_zero-2-0.pdf', MEMBER_TYPES.NON),
	'IODL-1.0': (STATIC_URL + 'metashare/licences/IODL-1.0.pdf', MEMBER_TYPES.NON),
	'NLOD-1.0': (STATIC_URL + 'metashare/licences/NLOD-1.0.pdf', MEMBER_TYPES.NON),
	'OGL-3.0': (STATIC_URL + 'metashare/licences/OGL-3.0.pdf', MEMBER_TYPES.NON),
	'NCGL-1.0': (STATIC_URL + 'metashare/licences/NCGL-1.0.pdf', MEMBER_TYPES.GOD),
	'openUnder-PSI': (STATIC_URL + 'metashare/licences/openUnderPSI.txt', MEMBER_TYPES.NON),
	'publicDomain': (STATIC_URL + 'metashare/licences/publicDomain.txt', MEMBER_TYPES.NON), #('', MEMBER_TYPES.NON),
	'non-standard/Other_Licence/Terms': ('', MEMBER_TYPES.NON),
	'underReview': ('', MEMBER_TYPES.GOD),
}


def _get_user_membership(user):
	"""
	Returns a `MEMBER_TYPES` type based on the permissions of the given
	authenticated user. 
	"""
	if user.has_perm('accounts.ms_full_member'):
		return MEMBER_TYPES.FULL
	elif user.has_perm('accounts.ms_associate_member'):
		return MEMBER_TYPES.ASSOCIATE
	return MEMBER_TYPES.NON


def _get_licences(resource, user_membership):
	"""
	Returns the licences under which a download/purchase of the given resource
	is possible for the given user membership.
	
	The result is a dictionary mapping from licence names to pairs. Each pair
	contains the corresponding `licenceInfoType_model`, the download location
	URLs and a boolean denoting whether the resource may (and can) be directly
	downloaded or if there need to be further negotiations of some sort.
	"""
	distribution_infos = tuple(resource.distributioninfotype_model_set.all())

	# licence_infos = tuple([(l_info, d_info.downloadLocation + d_info.executionLocation) \
	licence_infos = tuple([(l_info, d_info.downloadLocation + d_info.executionLocation) \
						   for d_info in distribution_infos for l_info in d_info.licenceInfo.all()])

	all_licenses = dict([(l_info.licence, (l_info, access_links)) \
						 for l_info, access_links in licence_infos])
	result = {}
	for name, info in all_licenses.items():
		
		l_info, access_links = info
		access = LICENCEINFOTYPE_URLS_LICENCE_CHOICES.get(name, None)
		if access == None:
			LOGGER.warn("Unknown license name discovered in the database for " \
						"object #{}: {}".format(resource.id, name))
			del all_licenses[name]
		elif user_membership >= access[1] \
				and (len(access_links) or resource.storage_object.get_download()):
			# the resource can be downloaded somewhere under the current license
			# terms and the user's membership allows her to immediately download
			# the resource
			result[name] = (l_info, access[0], True)
		else:
			# further negotiations are required with the current license
			result[name] = (l_info, access[0], False)
	return result


class ResourceComponentInlineFormSet(ReverseInlineFormSet):
    '''
    A formset with custom save logic for resources.
    '''
    def clean(self):
        actual_instance = self.get_actual_resourceComponentType()

        error_list = ''
        if isinstance(actual_instance, corpusInfoType_model):
            error_list = error_list + self.clean_corpus(actual_instance)
        elif isinstance(actual_instance, languageDescriptionInfoType_model):
            error_list = error_list + self.clean_langdesc(actual_instance)
        elif isinstance(actual_instance, lexicalConceptualResourceInfoType_model):
            error_list = error_list + self.clean_lexicon(actual_instance)
        elif isinstance(actual_instance, toolServiceInfoType_model):
            error_list = error_list + self.clean_toolservice(actual_instance)
        else:
            raise Exception, "unexpected resource component class type: {}".format(actual_instance.__class__.__name__)
        try:
            actual_instance.full_clean()
        except ValidationError:
            #raise ValidationError('The content of the {} general info is not valid.'.format(self.get_actual_resourceComponentType()._meta.verbose_name))
            #raise AssertionError("Meaningful error message for general info")
            error_list = error_list + 'The content of the {} general info is not valid.'.format(self.get_actual_resourceComponentType()._meta.verbose_name)

        if error_list != '':
            raise ValidationError(error_list)
        super(ResourceComponentInlineFormSet, self).clean()

    def clean_media(self, parent, fieldnames):
        '''
        Clean the list of media data in the XXMediaType parent object.
        '''

        error = ''
        for modelfieldname in fieldnames:
            if modelfieldname not in self.data:
                continue
            value = self.data[modelfieldname]
            if not value:
                error = error + format(modelfieldname) + ' error. '
        return error

    def clean_corpus_one2many(self, corpusmediatype):
        error = ''
        media = 'corpusTextInfo'
        flag = 'showCorpusTextInfo'
        if flag in self.data and self.data[flag]:
            num_infos = corpusmediatype.corpustextinfotype_model_set.all().count()
            if num_infos == 0:
                error += media + ' error. '
        media = 'corpusVideoInfo'
        flag = 'showCorpusVideoInfo'
        if flag in self.data and self.data[flag]:
            num_infos = corpusmediatype.corpusvideoinfotype_model_set.all().count()
            if num_infos == 0:
                error += media + ' error. '
        return error

    def clean_corpus(self, corpus):
        return self.clean_corpus_one2many(corpus.corpusMediaType) \
            + self.clean_media(corpus.corpusMediaType, \
             ('corpusAudioInfo', 'corpusImageInfo', 'corpusTextNumericalInfo', 'corpusTextNgramInfo'))

    def clean_langdesc(self, langdesc):
        return self.clean_media(langdesc.languageDescriptionMediaType, \
            ('languageDescriptionTextInfo', 'languageDescriptionVideoInfo', 'languageDescriptionImageInfo'))

    def clean_lexicon(self, lexicon):
        return self.clean_media(lexicon.lexicalConceptualResourceMediaType, \
             ('lexicalConceptualResourceTextInfo', 'lexicalConceptualResourceAudioInfo', \
              'lexicalConceptualResourceVideoInfo', 'lexicalConceptualResourceImageInfo'))

    def clean_toolservice(self, tool):
        return ''

    def save_media(self, parent, fieldnames):
        '''
        Save the list of media data in the XXMediaType parent object.
        '''
        for modelfieldname in fieldnames:
            if modelfieldname not in self.data:
                continue
            value = self.data[modelfieldname]
            if not value:
                continue
            modelfield = parent._meta.get_field(modelfieldname)
            child_id = int(value)
            child = modelfield.rel.to.objects.get(pk=child_id)
            setattr(parent, modelfieldname, child)
            parent.save()

    def save_corpus(self, corpus, commit):
        self.save_media(corpus.corpusMediaType, \
             ('corpusAudioInfo', 'corpusImageInfo', 'corpusTextNumericalInfo', 'corpusTextNgramInfo'))

    def save_langdesc(self, langdesc, commit):
        self.save_media(langdesc.languageDescriptionMediaType, \
            ('languageDescriptionTextInfo', 'languageDescriptionVideoInfo', 'languageDescriptionImageInfo'))

    def save_lexicon(self, lexicon, commit):
        self.save_media(lexicon.lexicalConceptualResourceMediaType, \
             ('lexicalConceptualResourceTextInfo', 'lexicalConceptualResourceAudioInfo', \
              'lexicalConceptualResourceVideoInfo', 'lexicalConceptualResourceImageInfo'))

    def save_toolservice(self, tool, commit):
        pass

    def get_actual_resourceComponentType(self):
        if not (self.forms and self.forms[0].instance):
            raise Exception, "Cannot save for unexisting instance"
        if self.forms[0].instance.pk is not None:
            actual_instance = self.forms[0].instance
        else:
            actual_instance = resourceComponentTypeType_model.objects.get(pk=self.data['resourceComponentId'])
            self.forms[0].instance = actual_instance # we need to use the resourceComponentType we created earlier
        actual_instance = actual_instance.as_subclass()
        return actual_instance

    def save(self, commit=True):
        actual_instance = self.get_actual_resourceComponentType()
        if isinstance(actual_instance, corpusInfoType_model):
            self.save_corpus(actual_instance, commit)
        elif isinstance(actual_instance, languageDescriptionInfoType_model):
            self.save_langdesc(actual_instance, commit)
        elif isinstance(actual_instance, lexicalConceptualResourceInfoType_model):
            self.save_lexicon(actual_instance, commit)
        elif isinstance(actual_instance, toolServiceInfoType_model):
            self.save_toolservice(actual_instance, commit)
        else:
            raise Exception, "unexpected resource component class type: {}".format(actual_instance.__class__.__name__)
        super(ResourceComponentInlineFormSet, self).save(commit)
        return (actual_instance,)

# pylint: disable-msg=R0901
class ResourceComponentInline(ReverseInlineModelAdmin):
    formset = ResourceComponentInlineFormSet
    def __init__(self,
                 parent_model,
                 parent_fk_name,
                 model, admin_site,
                 inline_type):
        super(ResourceComponentInline, self). \
            __init__(parent_model, parent_fk_name, model, admin_site, inline_type)
        self.template = 'repository/editor/resourceComponentInline.html'

# pylint: disable-msg=R0901
class IdentificationInline(ReverseInlineModelAdmin):
    readonly_fields = ('metaShareId',)

def check_resource_status(resource):
    '''
    Return the status of the given resource.

    '''
    if not hasattr(resource, 'storage_object'):
        raise NotImplementedError, "{0} has no storage object".format(resource)
    status = resource.storage_object.publication_status
    return status

def change_resource_status(resource, status, precondition_status=None):
    '''
    Change the status of the given resource to the new status given.

    If precondition_status is not None, then apply the change ONLY IF the
    current status of the resource is precondition_status; otherwise do nothing.
    The status of non-master copy resources is never changed.
    '''
    if not hasattr(resource, 'storage_object'):
        raise NotImplementedError, "{0} has no storage object".format(resource)
    if resource.storage_object.master_copy and \
      (precondition_status is None \
       or precondition_status == resource.storage_object.publication_status):
        resource.storage_object.publication_status = status
        resource.storage_object.save()
        # explicitly write metadata XML and storage object to the storage folder
        resource.storage_object.update_storage()
        return True
    return False


def has_edit_permission(request, res_obj):
    """
    Returns `True` if the given request has permission to edit the metadata
    for the current resource, `False` otherwise.
    """
    ##previously:
    #return request.user.is_active and (request.user.is_superuser \
    #    or request.user in res_obj.owners.all() ##if it is owner, only can edit if it is a reviewer....
    #    or request.user.groups.filter(name="reviewers").exists())

    ## A user only can edit a resource if it is a superuser or a reviewer
    return request.user.is_active and (request.user.is_superuser \
        or request.user.groups.filter(name="reviewers").exists())


def has_publish_permission(request, queryset):
    """
    Returns `True` if the given request has permission to change the publication
    status of all given language resources, `False` otherwise.
    """
    # if not request.user.is_superuser:
    #     for obj in queryset:
    #         res_groups = obj.editor_groups.all()
    #         # we only allow a user to ingest/publish/suspend a resource if she
    #         # is a manager of one of the resource's `EditorGroup`s
    #         if not any(res_group.name == mgr_group.managed_group.name
    #                    for res_group in res_groups
    #                    for mgr_group in EditorGroupManagers.objects.filter(name__in=
    #                        request.user.groups.values_list('name', flat=True))):
    #             return False
    if not request.user.is_staff or request.user.groups.filter(name='naps').exists():
            return False
    return True


class MetadataForm(forms.ModelForm):
    def save(self, commit=True):
        today = datetime.date.today()
        if not self.instance.metadataCreationDate:
            self.instance.metadataCreationDate = today
        self.instance.metadataLastDateUpdated = today
        return super(MetadataForm, self).save(commit)


class MetadataInline(ReverseInlineModelAdmin):
    form = MetadataForm
    readonly_fields = ('metadataCreationDate', 'metadataLastDateUpdated',)

def json_validator(data):
	try:
		data.json()
		return True
	except:
		return False

def add_files2zip(files_path, filezip):
	for root, dirs, files in os.walk(files_path):
		for f in files:
			filezip.write(os.path.join(root,f),f)
			
def add_rejected_files2zip(files_path, filezip):
	for root, dirs, files in os.walk(files_path):
		for f in files:
			filezip.write(os.path.join(root,f),'rejected/'+f)
			
def add_other_files2zip(files_path, filezip):
	for root, dirs, files in os.walk(files_path):
		for f in files:
			filezip.write(os.path.join(root,f),'other/'+f)
			
def prepare_error_zip(error_msg,resource_path,request):
	errorzip=zipfile.ZipFile(resource_path+'/archive.zip',mode='w')
	add_files2zip(resource_path+'/doc/input',errorzip)
	add_files2zip(resource_path+'/tm/input',errorzip)
	add_files2zip(resource_path+'/other',errorzip)
	error_log = open(os.path.join(resource_path,'error.log'), 'w')
	error_log.write(error_msg)
	error_log.close()
	errorzip.write(os.path.join(resource_path,'error.log'), 'error.log')
	#close zip file with processed resources
	errorzip.close()

class ResourceModelAdmin(SchemaModelAdmin): 

    haystack_connection = 'default'
    inline_type = 'stacked'
    custom_one2one_inlines = {'identificationInfo':IdentificationInline,
                              'resourceComponentType':ResourceComponentInline,
                              'metadataInfo':MetadataInline, }

    content_fields = ('resourceComponentType',)
    # list_display = ('__unicode__', 'id', 'resource_type', 'publication_status', 'resource_Owners', 'editor_Groups',)
    list_display = ('__unicode__', 'id', 'resource_type', 'publication_status', 'resource_Owners', 'validated')
    list_filter = ('storage_object__publication_status', ResourceTypeFilter, ValidatedFilter)
    actions = ('process_action','publish_action', 'suspend_action', 'ingest_action',
        'export_xml_action', 'delete', 'add_group', 'remove_group',
        'add_owner', 'remove_owner', 'process_resource')
    hidden_fields = ('storage_object', 'owners', 'editor_groups',)
    search_fields = ("identificationInfo__resourceName", "identificationInfo__resourceShortName", "identificationInfo__description", "identificationInfo__identifier")

    def process_action(self, request, queryset):
        getext = lambda file_object: os.path.splitext(file_object)[-1]
        tmextensions=[".tmx", ".sdltm"]
        docextensions=[ ".pdf", ".doc", ".docx", ".rtf", ".txt", ".odt"]
		
        from metashare.xml_utils import to_xml_string
        if has_publish_permission(request, queryset):
            successful = 0
            #messages.info(request,queryset)
            for obj in queryset:
				#variables to control tc errors
				errors=0
				error_msg=''
				if check_resource_status(obj)== INGESTED : #only (re)process INGESTED resources, published are suposed to be ok #or check_resource_status(obj)== PUBLISHED : #only process INGESTED or PUBLISHED resources
					messages.info(request,_('You are processing a resource. This may take some time...'))
					###DEBUGGING_INFO
					##PATH TO THE RESOURCE
					#messages.info(request,escape(obj.storage_object._storage_folder()))

					#messages.info(request,obj.metadataInfo)
					##XML INFO OF THE RESOURCE
					
					#messages.info(request,"info del request...")
					#messages.info(request,to_xml_string(obj.export_to_elementtree(),
					#                               encoding="utf-8").encode("utf-8"))#obj.export_to_elementtree())

					################
					resource_info=obj.export_to_elementtree()
					r_languages=[]
					for lang in resource_info.iter('languageInfo'):
						lang_id=lang.find('languageId').text
						r_languages.append(lang_id)
					'''DEBUGGING_INFO	
					#messages.info(request,"info de idiomas...")	
					#messages.info(request,r_languages)
					'''
					r_name=''
					for r_info in resource_info.iter('resourceName'):
						r_name=r_info.text
					###	DEBUG
					#messages.info(request,'####'+r_name)
					
					licence_info=''
					for l_info in resource_info.iter('licenceInfo'):
						licence_info+=l_info.find('licence').text+': '
						if l_info.find('otherLicenceName'):
							licence_info+=l_info.find('otherLicenceName').text
					###	DEBUG	
					#messages.info(request,'####'+licence_info)
					
					#get the resource storage folder path
					resource_path=obj.storage_object._storage_folder()
					#first process for this resource:
					#cp archive.zip to _archive.zip iif _archive.zip does not exist...
					if not os.path.isfile(resource_path+'/_archive.zip'): #save the resource source for possible later reprocessing steps
						copyfile(resource_path+'/archive.zip',resource_path+'/_archive.zip')
						#save also a copy of the original uploaded resource
						copyfile(resource_path+'/archive.zip',resource_path+'/_archive_origin.zip')
					#unzip always _archive.zip wich has always the source resource files; archive.zip can contain processed documents 

					resource_zip=zipfile.ZipFile(resource_path+'/_archive.zip','r')
					#and unzip the resource files into the corresponding /input folder
					resources=resource_zip.namelist()
					#create, if needed, the /tm /docs /other folder
					resource_tm_path=resource_path+'/tm'
					resource_doc_path=resource_path+'/doc'
					resource_other_path=resource_path+'/other'
					tmx_files=[]
					call_tm2tmx=0
					call_doc2tmx=0
					#prepare tc calls:
					for r in resources:
							#check the extension of the files
							#if it is a tm file:
							filext=getext(r)
							if filext in tmextensions:
								if  not os.path.isdir(resource_tm_path):
									os.makedirs(resource_tm_path)
									os.makedirs(resource_tm_path+'/input')
								resource_zip.extract(r,resource_tm_path+'/input')
								tmx_files.append(r)
								call_tm2tmx = call_tm2tmx + 1
							elif filext in docextensions: #if it is a doc file
								if not os.path.isdir(resource_doc_path):
									os.makedirs(resource_doc_path)
									os.makedirs(resource_doc_path+'/input')
								resource_zip.extract(r,resource_doc_path+'/input')
								call_doc2tmx = call_doc2tmx + 1
							else : #either case...
								if not os.path.isdir(resource_other_path):
									os.makedirs(resource_other_path)
								resource_zip.extract(r,resource_other_path)
					response_tm=''
					
					if call_tm2tmx > 0:
						#prepare the json for calling the tm2tmx tc for each tmx in tmx_files
						r_id=obj.storage_object.id
						r_overwrite='true'

						messages.info(request,"Processing resource with tm2tmx...")

						#for tm in tmx_files:
						r_input=resource_tm_path+'/input'#+tm
						tm_json= {'id':r_id, 'title': r_name ,'input':r_input,'overwrite':r_overwrite,'languages':r_languages, 'license':licence_info}
						
						try: 
							response_tm=requests.post(settings.TM2TMX_URL,json=tm_json)
							if json_validator(response_tm):
								if response_tm.json()["status"]=="Success":
									successful +=1
								else:
									messages.error(request,"Something went wrong when processing the resource with the tm2tmx toolchain.")
									error_msg=error_msg+"Something went wrong when processing the resource with the tm2tmx toolchain."+response_tm.json()["info"]+'\n'
									#ToDo: add timestamp info to error.log 
									errors+=1
							else:	
								messages.error(request,"Invalid json response from tm2tmx toolchain: "+response_tm.text)
								error_msg=error_msg+"Invalid json response from tm2tmx toolchain: "+response_tm.text+'\n'
								#ToDo: add timestamp info to error.log 
								errors+=1
						except: 
							messages.error(request,"The POST request to the tm2tmx toolchain has failed: \n"+response_tm)
							error_msg=error_msg+"The POST request to the tm2tmx toolchain has failed."+response_tm+"\n"
							#ToDo: add timestamp info to error.log 
							errors+=1
								
					response_doc=''	

					if call_doc2tmx > 0:
						#prepare the json for calling the doc2tmx tc
						r_id=obj.storage_object.id
						r_input=resource_doc_path+'/input'
						r_overwrite='true'
						doc_json={'id':r_id, 'title':r_name,'input':r_input,'overwrite':r_overwrite,'languages':r_languages, 'license':licence_info}
						messages.info(request,"Processing resource with doc2tmx...")
						
						try:
							response_doc=requests.post(settings.DOC2TMX_URL,json=doc_json)
							if json_validator(response_doc):
								if response_doc.json()["status"] == "Success":
									successful += 1
								else:
									messages.error(request,"Something went wrong when processing the resource with the doc2tmx toolchain.\n "+response_doc.json()["info"])
									error_msg=error_msg+"Something went wrong when processing the resource with the doc2tmx toolchain.\n "+response_doc.json()["info"]+"\n"
									#ToDo: add timestamp info to error.log 
									errors+=1
							else:
								messages.error(request,response_doc.text)
								messages.error(request,"Invalid json response from doc2tmx toolchain: "+response_doc.text)
								error_msg=error_msg+"Invalid json response from doc2tmx toolchain: "+response_doc.text+'\n'
								#ToDo: add timestamp info to error.log 
								errors+=1
								
						except:

							messages.error(request,"The POST request to the doc2tmx toolchain has failed.\n"+response_doc)
							error_msg=error_msg+"The POST request to the doc2tmx toolchain has failed.\n "+response_doc+'\n'
							#ToDo: add timestamp info to error.log 
							errors+=1
						
				#if something success-> create new archive.zip and replace the old one uploaded by the user 	
				# if any errors, then handle error reporting
				if errors > 0 or error_msg!='':
					#create the archive.zip with the original files and the error.log file
					prepare_error_zip(error_msg,resource_path,request)
				elif successful > 0:

					#create the archive.zip with the processed resources
					processed_zip=zipfile.ZipFile(resource_path+'/archive.zip',mode='w')

					if response_doc != '' and json_validator(response_doc):
						messages.info(request,response_doc.json()["info"])

						#if any rejected file and !E file(s) in output --> add input/into rejected/inside archive.zip
						if not os.listdir(response_doc.json()["output"]): 
							add_rejected_files2zip(r_input,processed_zip)							
						else: #if there are any produced output-> copy output and rejected file(s)
							add_files2zip(response_doc.json()["output"],processed_zip)
							add_rejected_files2zip(response_doc.json()["rejected"],processed_zip)

					if response_tm != '' and json_validator(response_tm):
						add_files2zip(response_tm.json()["output"],processed_zip)
						add_rejected_files2zip(response_tm.json()["rejected"],processed_zip)
					

					#if there are other files: add them as well
					add_files2zip(resource_other_path,processed_zip)
					
					#close zip file with processed resources
					processed_zip.close()

					
				else:
					if error_msg !='':
						prepare_error_zip(error_msg,resource_path,request)
					else:
						messages.error(request,
                           _('Only ingested resources can be re-processed.'))
        else:
            messages.error(request, _('You do not have the permission to ' \
                            'perform this action for all selected resources.'))

    process_action.short_description = _("Process selected ingested resources")

    def publish_action(self, request, queryset):
        if has_publish_permission(request, queryset):
            successful = 0

            from metashare.xml_utils import to_xml_string
            for obj in queryset:
                if change_resource_status(obj, status=PUBLISHED,
                                          precondition_status=INGESTED):
                    successful += 1
                    saveLRStats(obj, UPDATE_STAT, request)

                    resource_name=[u.find('resourceName').text for u in obj.export_to_elementtree().iter('identificationInfo')]
                    
                    #If successfully published, add to the archive.zip file the license documentation 
                    resource_info=obj.export_to_elementtree()
                    licences_name=[]
                    for lic in resource_info.iter('licenceInfo'):
                        lic_name=lic.find('licence').text
                        licences_name.append(lic_name)
                    user_membership = _get_user_membership(request.user)    
                    licences = _get_licences(obj,user_membership)    
                    resource_path=obj.storage_object._storage_folder()
                    lr_archive_zip=zipfile.ZipFile(resource_path+'/archive.zip', mode='a')
                    for l in licences_name:
                        l_info, access_links, access = licences[l]
                        #add access file to the lr.archive.zip file 
                        licence_path=ROOT_PATH+access_links
                        path, filename = os.path.split(licence_path)
                        lr_archive_zip.write(licence_path,'license_'+filename)
                    lr_archive_zip.close()
                    #send corresponding emails
                    emails=obj.owners.all().values_list('email',flat=True)
                    name=obj.owners.all().values_list('first_name',flat=True)
                    surname=obj.owners.all().values_list('last_name',flat=True)
                    
                    email_data={'resourcename':resource_name[0],'username':name[0], 'usersurname':surname[0]}
                    try:
                        send_mail('Published Resource', render_to_string('repository/published_resource.email',email_data) , settings.EMAIL_ADDRESSES['elri-no-reply'],emails, fail_silently=False)
                    except:
                        # failed to send e-mail to superuser
                        # If the email could not be sent successfully, tell the user
                        # about it and also give the confirmation URL.
                        messages.error(request,_("There was an error sending out the notification email to the resource owners. Please contact them directly."))
                        # Redirect the user to the front page. ?
                        #return redirect('metashare.views.frontpage')
            if successful > 0:
                messages.info(request, ungettext(
                    'Successfully published %(ingested)s ingested resource.',
                    'Successfully published %(ingested)s ingested resources.',
                    successful) % {'ingested': successful})
            else:
                messages.error(request,
                               _('Only ingested resources can be published.'))
           
        else:
            messages.error(request, _('You do not have the permission to ' \
                            'perform this action for all selected resources.'))

    publish_action.short_description = _("Publish selected ingested resources")

    def suspend_action(self, request, queryset):
        if has_publish_permission(request, queryset):
            successful = 0
            for obj in queryset:
                if change_resource_status(obj, status=INGESTED,
                                          precondition_status=PUBLISHED):
                    successful += 1
                    saveLRStats(obj, INGEST_STAT, request)
            if successful > 0:
                messages.info(request, ungettext(
                        'Successfully suspended %s published resource.',
                        'Successfully suspended %s published resources.',
                        successful) % (successful,))
            else:
                messages.error(request,
                    _('Only published resources can be suspended.'))
        else:
            messages.error(request, _('You do not have the permission to ' \
                            'perform this action for all selected resources.'))

    suspend_action.short_description = \
        _("Suspend selected published resources")

    def branch_lr(self, request,queryset):
        #implements automatic processing for ingested lr
        self.process_action(request,queryset)

    def ingest_action(self, request, queryset):

        if has_publish_permission(request, queryset) or request.user.is_staff:
            successful = 0
            resource_info=[]
            from metashare.xml_utils import to_xml_string
            for obj in queryset:
                if change_resource_status(obj, status=INGESTED,
                                          precondition_status=INTERNAL):
					successful += 1
					saveLRStats(obj, INGEST_STAT, request)
					resource_info.append(obj.export_to_elementtree())
					#get resource name to include in the email
					resource_name=[u.find('resourceName').text for u in obj.export_to_elementtree().iter('identificationInfo')]
					groups_name=[]
					for g in obj.groups.all():
						groups_name.append(g.name)
					##DEBUG
					#messages.info(request,groups_name)
					##
					#send an email to the reviewers related to the groups where the resource is published
					#get the emails of those users that are reviewers
					reviewers = [u.email for u in User.objects.filter(groups__name__in=['reviewers'])] #,groups__name__in=groups_name)]
					##DEBUG
					##group_users=[u.email for u in User.objects.filter(groups__name__in=groups_name)]
					##
					#get the emails of the reviewers that share groups with the resource
					group_reviewers = [u.email for u in User.objects.filter(groups__name__in=groups_name, email__in=reviewers)]
					#####DEBUG
					##messages.info(request,reviewers)
					##messages.info(request,group_users)
					##messages.info(request,group_reviewers)
					####
					#send the ingested resource notification mail
					email_data={'resourcename':resource_name[0]}
					try:
						send_mail("Ingested Resource", render_to_string('repository/ingested_resource.email',email_data),settings.EMAIL_ADDRESSES['elri-no-reply'],group_reviewers)
					except:
						# failed to send e-mail to superuser
						# If the email could not be sent successfully, tell the user
						# about it and also give the confirmation URL.
						messages.error(request,_("There was an error sending out the notification email to the group reviewers. Please contact them directly."))
						# Redirect the user to the front page. ?
						#return redirect('metashare.views.frontpage')
            if successful > 0:
                messages.info(request, ungettext(
                    'Successfully ingested %(internal)s internal resource.',
                    'Successfully ingested %(internal)s internal resources.',
                    successful) % {'internal': successful})
                #Implements the system branch 4 automatic lr processing
                self.branch_lr(request,queryset)

            else:
                messages.error(request,
                               _('Only internal resources can be ingested.'))
        else:
            messages.error(request, _('You do not have the permission to ' \
                            'perform this action for all selected resources.'))

    ingest_action.short_description = _("Ingest selected internal resources")



    def export_xml_action(self, request, queryset):
        from StringIO import StringIO
        from zipfile import ZipFile
        from django import http
        from metashare.xml_utils import to_xml_string

        zipfilename = "resources_export.zip"
        in_memory = StringIO()
        with ZipFile(in_memory, 'w') as zipfile:
            for obj in queryset:
                try:
                    xml_string = to_xml_string(obj.export_to_elementtree(),
                                               encoding="utf-8").encode("utf-8")
                    resource_filename = \
                        'resource-{0}.xml'.format(obj.storage_object.id)
                    zipfile.writestr(resource_filename, xml_string)

                except Exception:
                    return HttpResponseNotFound(_('Could not export resource "%(name)s" '
                        'with primary key %(key)s.') \
                            % {'name': force_unicode(obj),
                               'key': escape(obj.storage_object.id)})
            zipfile.close()

        response = http.HttpResponse()
        response['Content-Disposition'] = \
            'attachment; filename=%s' % (zipfilename)
        response['content_type'] = 'application/zip'
        in_memory.seek(0)
        response.write(in_memory.read())
        return response

    export_xml_action.short_description = \
        _("Export selected resource descriptions to XML")

    def resource_Owners(self, obj):
        """
        Method used for changelist view for resources.
        """
        owners = obj.owners.all()
        if owners.count() == 0:
            return None
        owners_list = ''
        for owner in owners.all():
            owners_list += owner.username + ', '
        owners_list = owners_list.rstrip(', ')
        return owners_list

    def editor_Groups(self, obj):
        """
        Method used for changelist view for resources.
        """
        editor_groups = obj.editor_groups.all()
        if editor_groups.count() == 0:
            return None
        groups_list = ''
        for group in editor_groups.all():
            groups_list += group.name + ', '
        groups_list = groups_list.rstrip(', ')
        return groups_list

    def validated(self, obj):
        """
        Method used for changelist view for resources.
        """
        return "YES" if obj.storage_object.get_validation() else "NO"

    class ConfirmDeleteForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    class IntermediateMultiSelectForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

        def __init__(self, choices = None, *args, **kwargs):
            super(ResourceModelAdmin.IntermediateMultiSelectForm, self).__init__(*args, **kwargs)
            if choices is not None:
                self.choices = choices
                self.fields['multifield'] = forms.ModelMultipleChoiceField(self.choices)

    @csrf_protect_m
    def delete(self, request, queryset):
        """
        Form to mark a resource as delete.
        """

        if not self.has_delete_permission(request):
            raise PermissionDenied
        if 'cancel' in request.POST:
            self.message_user(request,
                              _('Cancelled deleting the selected resources.'))
            return

        can_be_deleted = []
        cannot_be_deleted = []
        for resource in queryset:
            if self.has_delete_permission(request, resource):
                can_be_deleted.append(resource)
            else:
                cannot_be_deleted.append(resource)
        if 'delete' in request.POST:
            form = self.ConfirmDeleteForm(request.POST)
            if form.is_valid():
                from project_management.models import ManagementObject
                for resource in can_be_deleted:
                    self.delete_model(request, resource)
                    # PROJECT MANAGEMENT
                    # also delete related management object completely
                    try:
                        mng_obj = ManagementObject.objects.get(resource=resource)
                        mng_obj.delete()
                    except ObjectDoesNotExist:
                        pass
                count = len(can_be_deleted)
                messages.success(request,
                    ungettext('Successfully deleted %d resource.',
                              'Successfully deleted %d resources.', count)
                        % (count,))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.ConfirmDeleteForm(initial={admin.ACTION_CHECKBOX_NAME:
                            request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
                      'title': _('Are you sure?'),
                      'can_be_deleted': can_be_deleted,
                      'cannot_be_deleted': cannot_be_deleted,
                      'selected_resources': queryset,
                      'form': form,
                      'path': request.get_full_path()
                     }
        dictionary.update(create_breadcrumb_template_params(self.model, _('Delete resource')))

        return render_to_response('admin/repository/resourceinfotype_model/delete_selected_confirmation.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    delete.short_description = _("Mark selected resources as deleted")


    @csrf_protect_m
    def add_group(self, request, queryset):
        """
        Form to add an editor group to a resource.
        """

        if 'cancel' in request.POST:
            self.message_user(request, _('Cancelled adding editor groups.'))
            return
        elif 'add_editor_group' in request.POST:
            _addable_groups = \
                ResourceModelAdmin._get_addable_editor_groups(request.user)
            form = self.IntermediateMultiSelectForm(_addable_groups,
                request.POST)
            if form.is_valid():
                _successes = 0
                # actually this should be in the form validation but we just
                # make sure here that only addable groups are actually added
                groups = [g for g in form.cleaned_data['multifield']
                          if g in _addable_groups]
                for obj in queryset:
                    if request.user.is_superuser or obj.owners.filter(
                                    username=request.user.username).count():
                        obj.editor_groups.add(*groups)
                        obj.save()
                        _successes += 1
                _failures = queryset.count() - _successes
                if _failures:
                    messages.warning(request, _('Successfully added editor ' \
                        'groups to %(success)i of the selected resources. %(failure)i resource ' \
                        'editor groups were left unchanged due to missing ' \
                        'permissions.') % {"success":_successes, "failure":_failures})
                else:
                    messages.success(request, _('Successfully added editor ' \
                                        'groups to all selected resources.'))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.IntermediateMultiSelectForm(
                ResourceModelAdmin._get_addable_editor_groups(request.user),
                initial={admin.ACTION_CHECKBOX_NAME:
                         request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
                      'selected_resources': queryset,
                      'form': form,
                      'path': request.get_full_path()
                     }
        dictionary.update(create_breadcrumb_template_params(self.model, _('Add editor group')))

        return render_to_response('admin/repository/resourceinfotype_model/add_editor_group.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    add_group.short_description = _("Add editor groups to selected resources")

    @staticmethod
    def _get_addable_editor_groups(user):
        """
        Returns a queryset of the `EditorGroup` objects that the given user is
        allowed to add to a resource.

        Superusers can add all editor groups. Other users can only add those
        editor groups of which they are a member or a manager.
        """
        if user.is_superuser:
            return EditorGroup.objects.all()
        else:
            return EditorGroup.objects.filter(
                # either a group member
                Q(name__in=user.groups.values_list('name', flat=True))
                # or a manager of the editor group
              | Q(name__in=EditorGroupManagers.objects.filter(name__in=
                    user.groups.values_list('name', flat=True)) \
                        .values_list('managed_group__name', flat=True)))

    @csrf_protect_m
    def remove_group(self, request, queryset):
        """
        Form to remove an editor group from a resource.
        """

        if not request.user.is_superuser:
            raise PermissionDenied

        if 'cancel' in request.POST:
            self.message_user(request,
                              _('Cancelled removing editor groups.'))
            return
        elif 'remove_editor_group' in request.POST:
            query = EditorGroup.objects.all()
            form = self.IntermediateMultiSelectForm(query, request.POST)
            if form.is_valid():
                groups = form.cleaned_data['multifield']
                for obj in queryset:
                    obj.editor_groups.remove(*groups)
                    obj.save()
                self.message_user(request, _('Successfully removed ' \
                            'editor groups from the selected resources.'))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.IntermediateMultiSelectForm(EditorGroup.objects.all(),
                initial={admin.ACTION_CHECKBOX_NAME:
                         request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
                      'selected_resources': queryset,
                      'form': form,
                      'path': request.get_full_path()
                     }
        dictionary.update(create_breadcrumb_template_params(self.model, _('Remove editor group')))

        return render_to_response('admin/repository/resourceinfotype_model/'
                                  'remove_editor_group.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    remove_group.short_description = _("Remove editor groups from selected " \
                                       "resources")

    @csrf_protect_m
    def add_owner(self, request, queryset):
        """
        Form to add an owner to a resource.
        """

        if 'cancel' in request.POST:
            self.message_user(request, _('Cancelled adding owners.'))
            return
        elif 'add_owner' in request.POST:
            form = self.IntermediateMultiSelectForm(
                User.objects.filter(is_active=True), request.POST)
            if form.is_valid():
                _successes = 0
                owners = form.cleaned_data['multifield']
                for obj in queryset:
                    if request.user.is_superuser or obj.owners.filter(
                                    username=request.user.username).count():
                        obj.owners.add(*owners)
                        obj.save()
                        _successes += 1
                _failures = queryset.count() - _successes
                if _failures:
                    messages.warning(request, _('Successfully added owners ' \
                        'to %(success)i of the selected resources. %(failure)i resource owners ' \
                        'were left unchanged due to missing permissions.')
                        % {"success":_successes, "failure":_failures})
                else:
                    messages.success(request, _('Successfully added owners ' \
                                                'to all selected resources.'))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.IntermediateMultiSelectForm(
                User.objects.filter(is_active=True),
                initial={admin.ACTION_CHECKBOX_NAME:
                         request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
                      'selected_resources': queryset,
                      'form': form,
                      'path': request.get_full_path()
                     }
        dictionary.update(create_breadcrumb_template_params(self.model, _('Add owner')))

        return render_to_response('admin/repository/resourceinfotype_model/add_owner.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    add_owner.short_description = _("Add owners to selected resources")

    @csrf_protect_m
    def remove_owner(self, request, queryset):
        """
        Form to remove an owner from a resource.
        """

        if not request.user.is_superuser:
            raise PermissionDenied

        if 'cancel' in request.POST:
            self.message_user(request, _('Cancelled removing owners.'))
            return
        elif 'remove_owner' in request.POST:
            form = self.IntermediateMultiSelectForm(
                User.objects.filter(is_active=True), request.POST)
            if form.is_valid():
                owners = form.cleaned_data['multifield']
                for obj in queryset:
                    obj.owners.remove(*owners)
                    obj.save()
                self.message_user(request, _('Successfully removed owners ' \
                                             'from the selected resources.'))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.IntermediateMultiSelectForm(
                User.objects.filter(is_active=True),
                initial={admin.ACTION_CHECKBOX_NAME:
                         request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
                      'selected_resources': queryset,
                      'form': form,
                      'path': request.get_full_path()
                     }
        dictionary.update(create_breadcrumb_template_params(self.model, _('Remove owner')))

        return render_to_response('admin/repository/resourceinfotype_model/remove_owner.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    remove_owner.short_description = _("Remove owners from selected resources")

    def get_urls(self):
        from django.conf.urls import patterns, url
        urlpatterns = super(ResourceModelAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = patterns('',
            url(r'^(.+)/upload-data/$',
                wrap(self.uploaddata_view),
                name='%s_%s_uploaddata' % info),
            url(r'^(.+)/datadl/$',
                self.datadl,
            # VALIDATION REPORT
                name='%s_%s_datadl' % info),
            url(r'^(.+)/upload-report/$',
                wrap(self.uploadreport_view),
                name='%s_%s_uploadreport' % info),
            url(r'^(.+)/reportdl/$',
                wrap(self.reportdl),
                name='%s_%s_reportdl' % info),
            # MANUAL VALIDATION
            url(r'^(.+)/validaterl/$',
                wrap(self.validaterl),
                name="%s_%s_validaterl" % info),
            # LEGAL DOCUMENTATION
            url(r'^(.+)/upload-legal/$',
                wrap(self.uploadlegal_view),
                name='%s_%s_uploadlegal' % info),
            url(r'^(.+)/legaldl/$',
                wrap(self.legaldl),
                name='%s_%s_legaldl' % info),
            url(r'^my/$',
                wrap(self.changelist_view_filtered),
                name='%s_%s_myresources' % info),
            url(r'^(.+)/export-xml/$',
                wrap(self.exportxml),
                name='%s_%s_exportxml' % info),
        ) + urlpatterns
        return urlpatterns

    @csrf_protect_m
    def changelist_view_filtered(self, request, extra_context=None):
        '''
        The filtered changelist view for My Resources.
        We reuse the generic django changelist_view and squeeze in our wish to
        show the filtered view in two places:
        1. we patch request.POST to insert a parameter 'myresources'='true',
        which will be interpreted in get_changelist to show the filtered
        version;
        2. we pass a extra_context variable 'myresources' which will be
        interpreted in the template change_list.html.
        '''
        _post = request.POST.copy()
        _post['myresources'] = 'true'
        request.POST = _post
        _extra_context = extra_context or {}
        _extra_context.update({'myresources':True})
        return self.changelist_view(request, _extra_context)

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        if 'myresources' in request.POST:
            return FilteredChangeList
        else:
            return AllChangeList

    @csrf_protect_m
    def uploaddata_view(self, request, object_id, extra_context=None):
        """
        The 'upload data' admin view for resourceInfoType_model instances.
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s does not exist.') \
             % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        storage_object = obj.storage_object
        if storage_object is None:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s does not have a StorageObject attached.') \
              % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if not storage_object.master_copy:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s is not a master-copy.') \
              % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        existing_download = storage_object.get_download()
        storage_folder = storage_object._storage_folder()

        if request.method == 'POST':
            form = StorageObjectUploadForm(request.POST, request.FILES)
            form_validated = form.is_valid()

            if form_validated:
                # Check if a new file has been uploaded to resource.
                resource = request.FILES['resource']
                _extension = None
                for _allowed_extension in ALLOWED_ARCHIVE_EXTENSIONS:
                    if resource.name.endswith(_allowed_extension):
                        _extension = _allowed_extension
                        break

                # We can assert that an extension has been found as the form
                # validation would have raise a ValidationError otherwise;
                # still, we raise an AssertionError if anything goes wrong!
                assert(_extension in ALLOWED_ARCHIVE_EXTENSIONS)

                if _extension:
                    _storage_folder = storage_object._storage_folder()
                    _out_filename = '{}/archive.{}'.format(_storage_folder,
                      _extension)

                    # Copy uploaded file to storage folder for this object.
                    with open(_out_filename, 'wb') as _out_file:
                        # pylint: disable-msg=E1101
                        for _chunk in resource.chunks():
                            _out_file.write(_chunk)
                            
                    #save a copy of the uploaded files to allow reprocessing         
                    copyfile(_out_filename, '{}/_archive.{}'.format(_storage_folder,
                      _extension))
                    # Update the corresponding StorageObject to update its
                    # download data checksum.
                    obj.storage_object.compute_checksum()
                    obj.storage_object.save()

                    change_message = 'Uploaded "{}" to "{}" in {}.'.format(
                      resource.name, storage_object._storage_folder(),
                      storage_object)

                    self.log_change(request, obj, change_message)

                return self.response_change(request, obj)

        else:
            form = StorageObjectUploadForm()

        context = {
            'title': _('Upload resource: "%s"') % force_unicode(obj),
            'form': form,
            'storage_folder': storage_folder,
            'existing_download': existing_download,
            'object_id': object_id,
            'original': obj,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        context_instance = RequestContext(request,
          current_app=self.admin_site.name)
        return render_to_response(
          ['admin/repository/resourceinfotype_model/upload_resource.html'], context,
          context_instance)

    ## VALIDATION REPORT
    @csrf_protect_m
    def uploadreport_view(self, request, object_id, extra_context=None):
        """
        The 'upload validation' admin view for resourceInfoType_model instances.
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)s does not exist.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        storage_object = obj.storage_object
        if storage_object is None:
            raise Http404(_('%(name)s object with primary key %(key)s does not have a StorageObject attached.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if not storage_object.master_copy:
            raise Http404(_('%(name)s object with primary key %(key)s is not a master-copy.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        existing_validation = storage_object.get_validation()
        storage_folder = storage_object._storage_folder()

        if request.method == 'POST':
            form = ValidationUploadForm(request.POST, request.FILES)
            form_validated = form.is_valid()

            if form_validated:
                # Check if a new file has been uploaded to resource.
                report = request.FILES['report']
                _extension = None
                for _allowed_extension in ALLOWED_VALIDATION_EXTENSIONS:
                    if report.name.endswith(_allowed_extension):
                        _extension = _allowed_extension
                        break

                # We can assert that an extension has been found as the form
                # validation would have raise a ValidationError otherwise;
                # still, we raise an AssertionError if anything goes wrong!
                assert (_extension in ALLOWED_VALIDATION_EXTENSIONS)

                if _extension:
                    _storage_folder = storage_object._storage_folder()

                    _out_filename = u'{}/ELRI_VALREP_{}_{}.{}'.format(_storage_folder,
                                                                      object_id,
                                                                      obj.identificationInfo.resourceName['en']
                                                                      .replace(u"/", u"_").replace(u" ", u"_"),
                                                                      _extension)
					#_out_filename = u'{}/ELRC_VALREP_{}_{}.{}'.format(_storage_folder,
                    #                                                  object_id,
                    #                                                  obj.identificationInfo.resourceName['en']
                    #                                                  .replace(u"/", u"_").replace(u" ", u"_"),
                    #                                                  _extension)
                    
                    # we need to make sure the any existing report is removed
                    # while the new one may have a different filename due to
                    # resourceName change
                    if existing_validation:
                        import os
                        os.remove(existing_validation)

                    # Copy uploaded file to storage folder for this object.
                    with open(_out_filename.encode('utf-8'), 'wb') as _out_file:
                        # pylint: disable-msg=E1101
                        for _chunk in report.chunks():
                            _out_file.write(_chunk)

                    # TODO: resource.name may contain unicode characters which throw UnicodeEncodeError
                    change_message = u'Uploaded "{}" to "{}" in {}.'.format(
                        report.name, storage_object._storage_folder(),
                        storage_object)

                    self.log_change(request, obj, change_message)

                return self.response_change(request, obj)

        else:
            form = ValidationUploadForm()

        context = {
            'title': _('Upload validation report: "%s"') % force_unicode(obj),
            'form': form,
            'storage_folder': storage_folder,
            'existing_validation': existing_validation,
            'object_id': object_id,
            'original': obj,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        context_instance = RequestContext(request,
                                          current_app=self.admin_site.name)
        return render_to_response(
            ['admin/repository/resourceinfotype_model/upload_report.html'], context,
            context_instance)

    ## VALIDATION REPORT
    @csrf_protect_m
    def reportdl(self, request, object_id, extra_context=None):

        # return HttpResponse("OK")
        """
        Returns an HTTP response with a download of the given validation report.
        """

        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))
        storage_object = obj.storage_object
        dl_path = storage_object.get_validation()
        if dl_path:
            try:
                def dl_stream_generator():
                    with open(dl_path, 'rb') as _local_data:
                        _chunk = _local_data.read(4096)
                        while _chunk:
                            yield _chunk
                            _chunk = _local_data.read(4096)

                # build HTTP response with a guessed mime type; the response
                # content is a stream of the download file
                filemimetype = guess_type(dl_path)[0] or "application/octet-stream"
                response = HttpResponse(dl_stream_generator(),
                                        content_type=filemimetype)
                response['Content-Length'] = getsize(dl_path)
                response['Content-Disposition'] = 'attachment; filename={0}' \
                    .format(split(dl_path)[1])
                # LOGGER.info("Offering a local editor download of resource #{0}." \
                #             .format(object_id))
                return response
            except:
                pass

        # no download could be provided
        return render_to_response('repository/report_not_downloadable.html',
                                  {'resource': obj, 'reason': 'internal'},
                                  context_instance=RequestContext(request))

    @csrf_protect_m
    def validaterl(self, request, object_id, extra_context=None):
        raise Http404

    ## LEGAL DOCUMENTATION
    @csrf_protect_m
    def uploadlegal_view(self, request, object_id, extra_context=None):
        """
        The 'upload data' admin view for resourceInfoType_model instances.
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)s does not exist.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        storage_object = obj.storage_object
        if storage_object is None:
            raise Http404(_('%(name)s object with primary key %(key)s does not have a StorageObject attached.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if not storage_object.master_copy:
            raise Http404(_('%(name)s object with primary key %(key)s is not a master-copy.') \
                          % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        existing_legal = storage_object.get_legal_documentation()
        storage_folder = storage_object._storage_folder()

        if request.method == 'POST':
            form = LegalDocumetationUploadForm(request.POST, request.FILES)
            form_validated = form.is_valid()

            if form_validated:
                # Check if a new file has been uploaded to resource.
                legal_documentation = request.FILES['legalDocumentation']
                _extension = None
                for _allowed_extension in ALLOWED_LEGAL_DOCUMENTATION_EXTENSIONS:
                    if legal_documentation.name.endswith(_allowed_extension):
                        _extension = _allowed_extension
                        break

                # We can assert that an extension has been found as the form
                # validation would have raise a ValidationError otherwise;
                # still, we raise an AssertionError if anything goes wrong!
                assert (_extension in ALLOWED_LEGAL_DOCUMENTATION_EXTENSIONS)

                if _extension:
                    _storage_folder = storage_object._storage_folder()
                    _out_filename = '{}/legal_documentation.{}'.format(_storage_folder,
                                                                       _extension)

                    # Copy uploaded file to storage folder for this object.
                    with open(_out_filename, 'wb') as _out_file:
                        # pylint: disable-msg=E1101
                        for _chunk in legal_documentation.chunks():
                            _out_file.write(_chunk)

                    # Update the corresponding StorageObject to update its
                    # download data checksum.
                    # obj.storage_object.compute_checksum()
                    # obj.storage_object.save()

                    # TODO: resource.name may contain unicode characters which throw UnicodeEncodeError
                    change_message = 'Uploaded "{}" to "{}" in {}.'.format(
                        legal_documentation.name, storage_object._storage_folder(),
                        storage_object)

                    self.log_change(request, obj, change_message)

                return self.response_change(request, obj)

        else:
            form = LegalDocumetationUploadForm()

        context = {
            'title': _('Upload legal documentation: "%s"') % force_unicode(obj),
            'form': form,
            'storage_folder': storage_folder,
            'existing_legal': existing_legal,
            'object_id': object_id,
            'original': obj,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        context_instance = RequestContext(request,
                                          current_app=self.admin_site.name)
        return render_to_response(
            ['admin/repository/resourceinfotype_model/upload_legal.html'], context,
            context_instance)

    ## LEGAL DOCUMENTATION
    @csrf_protect_m
    def legaldl(self, request, object_id, extra_context=None):

        # return HttpResponse("OK")
        """
        Returns an HTTP response with a download of the given legal documentation.
        """

        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))
        storage_object = obj.storage_object
        dl_path = storage_object.get_legal_documentation()
        if dl_path:
            try:
                def dl_stream_generator():
                    with open(dl_path, 'rb') as _local_data:
                        _chunk = _local_data.read(4096)
                        while _chunk:
                            yield _chunk
                            _chunk = _local_data.read(4096)

                # build HTTP response with a guessed mime type; the response
                # content is a stream of the download file
                filemimetype = guess_type(dl_path)[0] or "application/octet-stream"
                response = HttpResponse(dl_stream_generator(),
                                        content_type=filemimetype)
                response['Content-Length'] = getsize(dl_path)
                response['Content-Disposition'] = 'attachment; filename={0}' \
                    .format(split(dl_path)[1])
                # LOGGER.info("Offering a local editor download of resource #{0}." \
                #             .format(object_id))
                return response
            except:
                pass

        # no download could be provided
        return render_to_response('repository/legal_not_downloadable.html',
                                  {'resource': obj, 'reason': 'internal'},
                                  context_instance=RequestContext(request))

    @csrf_protect_m
    def datadl(self, request, object_id, extra_context=None):

        # return HttpResponse("OK")
        """
        Returns an HTTP response with a download of the given resource.
        """

        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))
        if obj is not None:
            storage_object = obj.storage_object
            dl_path = storage_object.get_download()
            if dl_path:
                try:
                    def dl_stream_generator():
                        with open(dl_path, 'rb') as _local_data:
                            _chunk = _local_data.read(4096)
                            while _chunk:
                                yield _chunk
                                _chunk = _local_data.read(4096)

                    # build HTTP response with a guessed mime type; the response
                    # content is a stream of the download file
                    filemimetype = guess_type(dl_path)[0] or "application/octet-stream"
                    response = HttpResponse(dl_stream_generator(),
                                            content_type=filemimetype)
                    response['Content-Length'] = getsize(dl_path)
                    response['Content-Disposition'] = 'attachment; filename={0}' \
                        .format(split(dl_path)[1])
                    # LOGGER.info("Offering a local editor download of resource #{0}." \
                    #             .format(object_id))
                    return response
                except:
                    pass
        # no download could be provided
        return render_to_response('repository/lr_not_downloadable.html',
                                  {'resource': obj, 'reason': 'internal'},
                                  context_instance=RequestContext(request))

    @csrf_protect_m
    def exportxml(self, request, object_id, extra_context=None):
        """
        Export the XML description for one single resource
        """
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s does not exist.') \
             % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if obj.storage_object is None:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s does not have a StorageObject attached.') \
              % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})
        elif obj.storage_object.deleted:
            return HttpResponseNotFound(_('%(name)s object with primary key %(key)s does not exist anymore.') \
              % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        from metashare.xml_utils import to_xml_string
        from django import http

        try:
            root_node = obj.export_to_elementtree()
            xml_string = to_xml_string(root_node, encoding="utf-8").encode('utf-8')
            resource_filename = 'resource-{0}.xml'.format(object_id)

            response = http.HttpResponse(xml_string, content_type='text/xml')
            response['Content-Disposition'] = 'attachment; filename=%s' % (resource_filename)
            return response

        except Exception:
            return HttpResponseNotFound(_('Could not export resource "%(name)s" with primary key %(key)s.') \
              % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

    def build_fieldsets_from_schema(self, include_inlines=False, inlines=()):
        """
        Builds fieldsets using SchemaModel.get_fields().
        """
        # pylint: disable-msg=E1101
        verify_subclass(self.model, SchemaModel)

        exclusion_list = set(self.get_excluded_fields() + self.get_hidden_fields() + self.get_non_editable_fields())

        _fieldsets = []
        _content_fieldsets = []
        # pylint: disable-msg=E1101
        _fields = self.model.get_fields()
        _has_content_fields = hasattr(self, 'content_fields')
        for _field_status in ('required', 'recommended', 'optional'):
            _visible_fields = []
            _visible_fields_verbose_names = []
            _visible_content_fields = []
            # pylint: disable-msg=C0103
            _visible_content_fields_verbose_names = []

            for _field_name in _fields[_field_status]:
                _is_visible = False
                if self.is_visible_as_normal_field(_field_name, exclusion_list):
                    _is_visible = True
                    _fieldname_to_append = _field_name
                elif self.is_visible_as_inline(_field_name, include_inlines, inlines):
                    _is_visible = True
                    _fieldname_to_append = encode_as_inline(_field_name)

                # Now, where to show the field: in administrative or in content fieldset:
                if _has_content_fields and _field_name in self.content_fields:
                    _relevant_fields = _visible_content_fields
                    _verbose_names = _visible_content_fields_verbose_names
                else:
                    _relevant_fields = _visible_fields
                    _verbose_names = _visible_fields_verbose_names

                # And now put the field where it belongs:
                if _is_visible:
                    _relevant_fields.append(_fieldname_to_append)
                    _verbose_names.append(self.model.get_verbose_name(_field_name))

            if len(_visible_fields) > 0:
                _detail = ', '.join(_visible_fields_verbose_names)
                _caption = u'{0} administration information: {1}'.format(_field_status.capitalize(), _detail)
                _fieldset = {'fields': _visible_fields}
                _fieldsets.append((_caption, _fieldset))
            if len(_visible_content_fields) > 0:
                _caption = u'{0} content information: {1}'.format(_field_status.capitalize(), '')
                _fieldset = {'fields': _visible_content_fields}
                _content_fieldsets.append((_caption, _fieldset))

        _fieldsets += _content_fieldsets

        _hidden_fields = self.get_hidden_fields()
        if _hidden_fields:
            _fieldsets.append((None, {'fields': _hidden_fields, 'classes':('display_none',)}))
        return _fieldsets

    def resource_type_selection_view(self, request, form_url, extra_context):
        opts = self.model._meta
        media = self.media or []
        context = {
            'title': 'Add %s' % force_unicode(opts.verbose_name),
            'show_delete': False,
            'app_label': opts.app_label,
            'media': mark_safe(media),
            'add': True,
            'has_add_permission': self.has_add_permission(request),
            'opts': opts,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'kb_link': settings.KNOWLEDGE_BASE_URL,
            'comp_name': _('%s') % force_unicode(opts.verbose_name),
        }
        if extra_context:
            context.update(extra_context)
        return render_to_response("repository/editor/select_resource_type.html", context, RequestContext(request))

    def copy_show_media(self, post):
        showtags = ('showCorpusTextInfo', 'showCorpusAudioInfo', 'showCorpusVideoInfo', 'showCorpusImageInfo', 'showCorpusTextNumericalInfo',
                 'showCorpusTextNgramInfo',
                 'showLangdescTextInfo', 'showLangdescVideoInfo', 'showLangdescImageInfo',
                 'showLexiconTextInfo', 'showLexiconAudioInfo', 'showLexiconVideoInfo', 'showLexiconImageInfo',
                 )
        out = {}
        for item in showtags:
            if item in post:
                out[item] = True
        return out

    def get_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site.

        This is used by changelist_view, for example, but also for determining
        whether the current user may edit a resource or not.
        """
        result = super(ResourceModelAdmin, self).get_queryset(request)
        # filter results marked as deleted:
        result = result.distinct().filter(storage_object__deleted=False)
        # all users but the superusers may only see resources for which they are
        # either owner or editor group member:
        if not request.user.is_superuser \
                and not request.user.groups.filter(name='reviewers').exists():
            if request.user.is_authenticated():
                result = result.distinct().filter(Q(owners=request.user)
                        | Q(editor_groups__name__in=
                                request.user.groups.values_list('name', flat=True))
                        | Q(groups__name__in=
                                request.user.groups.values_list('name', flat=True)))
            else:
                result = result.none()
        return result

    def has_delete_permission(self, request, obj=None):
        """
        Returns `True` if the given request has permission to change the given
        Django model instance.
        """
        result = super(ResourceModelAdmin, self) \
            .has_delete_permission(request, obj)
        if result and obj:
            if request.user.is_superuser:
                return True
            # in addition to the default delete permission determination, we
            # only allow a user to delete a resource if either:
            # (1) she is owner of the resource and the resource has not been
            #     ingested, yet
            # (2) she is a manager of one of the resource's `EditorGroup`s
            # (3) she is active and a reviewer (member of the "reviewers"
            # group), and the resource is internal or ingested)
            res_groups = obj.editor_groups.all()
            return (request.user in obj.owners.all()
                    and obj.storage_object.publication_status == INTERNAL) \
                or any(res_group.name == mgr_group.managed_group.name
                       for res_group in res_groups
                       for mgr_group in EditorGroupManagers.objects.filter(name__in=
                            request.user.groups.values_list('name', flat=True))) \
                or (request.user.is_active and
                    request.user.groups.filter(name='reviewers').exists()
                    and obj.storage_object.publication_status in (INTERNAL,
                                                                  INGESTED))
        return result

    def get_actions(self, request):
        """
        Return a dictionary mapping the names of all actions for this
        `ModelAdmin` to a tuple of (callable, name, description) for each
        action.
        """
        result = super(ResourceModelAdmin, self).get_actions(request)
        # always remove the standard Django bulk delete action for resources (if
        # it hasn't previously been removed, yet)
        if 'delete_selected' in result:
            del result['delete_selected']
        if not request.user.is_superuser:
            del result['remove_group']
            del result['remove_owner']
            # TODO: revisit
            # if not 'myresources' in request.POST:
            #     del result['add_group']
            #     del result['add_owner']
            # only users with delete permissions can see the delete action:
            if not self.has_delete_permission(request):
                del result['delete']
            # only users who are the manager of some group can see the
            # ingest/publish/suspend actions:
            # and the process action as well
            if not request.user.is_staff:
                for action in (self.publish_action, self.suspend_action,self.process_action,):
                    del result[action.__name__]
        if request.user.groups.filter(name='naps').exists():
            del result['process_action']
            del result['publish_action']
            del result['suspend_action']
            del result['add_group']
            del result['add_owner']
        return result

    def create_hidden_structures(self, request):
        '''
        For a new resource of the given resource type, create the
        hidden structures needed and return them as a dict.
        '''
        resource_type = request.POST['resourceType']
        structures = {}
        if resource_type == 'corpus':
            corpus_media_type = corpusMediaTypeType_model.objects.create()
            corpus_info = corpusInfoType_model.objects.create(corpusMediaType=corpus_media_type)
            structures['resourceComponentType'] = corpus_info
            structures['corpusMediaType'] = corpus_media_type
        elif resource_type == 'langdesc':
            language_description_media_type = languageDescriptionMediaTypeType_model.objects.create()
            langdesc_info = languageDescriptionInfoType_model.objects.create(languageDescriptionMediaType=language_description_media_type)
            structures['resourceComponentType'] = langdesc_info
            structures['languageDescriptionMediaType'] = language_description_media_type
        elif resource_type == 'lexicon':
            lexicon_media_type = lexicalConceptualResourceMediaTypeType_model.objects.create()
            lexicon_info = lexicalConceptualResourceInfoType_model.objects.create(lexicalConceptualResourceMediaType=lexicon_media_type)
            structures['resourceComponentType'] = lexicon_info
            structures['lexicalConceptualResourceMediaType'] = lexicon_media_type
        elif resource_type == 'toolservice':
            tool_info = toolServiceInfoType_model.objects.create()
            structures['resourceComponentType'] = tool_info
            structures['toolServiceInfoId'] = tool_info.pk
        else:
            raise NotImplementedError, "Cannot deal with '{}' resource types just yet".format(resource_type)
        return structures

    def get_hidden_structures(self, request, resource=None):
        '''
        For a resource with existing hidden structures,
        fill a dict with the hidden objects.
        '''
        def get_mediatype_id(media_type_name, media_type_field):
            if media_type_name in request.POST:
                return request.POST[media_type_name]
            if media_type_field:
                return media_type_field.pk
            return ''
        resource_component_id = self.get_resource_component_id(request, resource)
        structures = {}
        resource_component = resourceComponentTypeType_model.objects.get(pk=resource_component_id)
        content_info = resource_component.as_subclass()
        structures['resourceComponentType'] = content_info
        if isinstance(content_info, corpusInfoType_model):
            structures['corpusMediaType'] = content_info.corpusMediaType
        elif isinstance(content_info, languageDescriptionInfoType_model):
            structures['langdescTextInfoId'] = get_mediatype_id('languageDescriptionTextInfo', \
                content_info.languageDescriptionMediaType.languageDescriptionTextInfo)
        elif isinstance(content_info, lexicalConceptualResourceInfoType_model):
            structures['lexiconTextInfoId'] = get_mediatype_id('lexicalConceptualResourceTextInfo', \
                content_info.lexicalConceptualResourceMediaType.lexicalConceptualResourceTextInfo)
        elif isinstance(content_info, toolServiceInfoType_model):
            structures['toolServiceInfoId'] = content_info.pk

        else:
            raise NotImplementedError, "Cannot deal with '{}' resource types just yet".format(content_info.__class__.__name__)
        return structures

    def get_resource_component_id(self, request, resource=None):
        '''
        For the given resource (if any) and request, try to get a resource component ID.
        '''
        if resource is not None:
            return resource.resourceComponentType.pk
        if request.method == 'POST':
            return request.POST['resourceComponentId']
        return None

    def add_user_to_resource_owners(self, request):
        '''
        Add the current user to the list of owners for the current resource and
        the user's `EditorGroup`s to the resource' editor_groups list.

        Due to the validation logic of django admin, we add the user/groups to
        the form's clean_data object rather than the resource object's m2m
        fields; the actual fields will be filled in save_m2m().
        '''
        # Preconditions:
        if not request.user or not request.POST:
            return
        user_id = str(request.user.pk)
        owners = request.POST.getlist('owners')
        # Target state already met:
        if user_id in owners:
            return

        # Get UserProfile instance corresponding to the current user.
        profile = request.user.userprofile

        # Need to add user to owners and groups to editor_groups
        owners.append(user_id)
        editor_groups = request.POST.getlist('editor_groups')
        editor_groups.extend(EditorGroup.objects \
            .filter(name__in=profile.default_editor_groups.values_list('name', flat=True))
            .values_list('pk', flat=True))

        _post = request.POST.copy()
        _post.setlist('owners', owners)
        _post.setlist('editor_groups', editor_groups)
        request.POST = _post

    @method_decorator(permission_required('repository.add_resourceinfotype_model'))
    def add_view(self, request, form_url='', extra_context=None):
        _extra_context = extra_context or {}
        _extra_context.update({'DJANGO_BASE':settings.DJANGO_BASE})

        # First, we show the resource type selection view:
        if not request.POST:
            return self.resource_type_selection_view(request, form_url, extra_context)
        # When we get that one back, we create any hidden structures:
        _extra_context.update(self.copy_show_media(request.POST))
        if 'resourceType' in request.POST:
            _structures = self.create_hidden_structures(request)
            _extra_context.update(_structures)
            request.method = 'GET' # simulate a first call to add/
        else:
            _structures = self.get_hidden_structures(request)
            _extra_context.update(_structures)
        # We add the current user to the resource owners:
        self.add_user_to_resource_owners(request)
        # And in any case, we serve the usual change form if we have a post request
        return super(ResourceModelAdmin, self).add_view(request, form_url, _extra_context)

    def save_model(self, request, obj, form, change):
        super(ResourceModelAdmin, self).save_model(request, obj, form, change)
        # update statistics
        if hasattr(obj, 'storage_object') and obj.storage_object is not None:
            saveLRStats(obj, UPDATE_STAT, request)

    def delete_model(self, request, obj):
        obj.storage_object.deleted = True
        obj.storage_object.save()
        obj.save()
        # explicitly write metadata XML and storage object to the storage folder
        obj.storage_object.update_storage()
        # update statistics
        saveLRStats(obj, DELETE_STAT, request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.model
        opts = model._meta
        obj = self.get_object(request, unquote(object_id))

        if obj is None:
                raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                    'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        _extra_context = extra_context or {}
        _extra_context.update({'DJANGO_BASE':settings.DJANGO_BASE})
        _structures = self.get_hidden_structures(request, obj)
        _extra_context.update(_structures)
        return super(ResourceModelAdmin, self).change_view(request, object_id, form_url, _extra_context)


class LicenceForm(forms.ModelForm):
    class Meta:
        model = licenceInfoType_model
        exclude = ()


class LicenceModelAdmin(SchemaModelAdmin):
    form = LicenceForm
