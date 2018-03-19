import datetime

import StringIO

import xlsxwriter
from django.core.mail import EmailMessage
from django.core.management import BaseCommand
from django.http import HttpResponse
from django.utils.encoding import smart_str
from metashare.local_settings import ILSP_ADMINS
from metashare.repository.models import resourceInfoType_model
from metashare.repository.views import _get_resource_linguality, _get_resource_lang_info, _get_resource_sizes, \
    _get_preferred_size, _get_resource_domain_info
from metashare.utils import prettify_camel_case_string
from project_management.models import _get_country


def _is_processed(r):
    relations = [relation.relationType for relation in r.relationinfotype_model_set.all() if
                 relation.relationType.startswith('is')]
    if (len(relations) > 1 and u"isPartOf" in relations) or len(relations) == 1:
        return True
    return False


def _is_not_processed_or_related(r):
    related_ids = set()
    if r.relationinfotype_model_set.all():
        related_ids = set([rel.relatedResource.targetResourceNameURI for rel in r.relationinfotype_model_set.all()])
    if related_ids:
        return False
    return True


def _cefdigital_report():
    '''
    Returns all resources in the repository as an excel file with
    predefined data to include.
    Get from url the 'email_to' variable
    '''
    now = datetime.datetime.now()
    then = now - datetime.timedelta(days=15)
    # get all resources and filter further
    resources = resourceInfoType_model.objects.filter(
        storage_object__deleted=False)
    unique_resources = []

    for r in resources:
        if _is_processed(r) or _is_not_processed_or_related(r):
            unique_resources.append(r)

    if len(unique_resources) > 0:
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)

        ## formating
        heading = workbook.add_format(
            {'font_size': 11, 'font_color': 'white', 'bold': True, 'bg_color': "#058DBE", 'border': 1})
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'yyyy, mmmm d'})
        title = "ELRC-SHARE_CEF-DIGITAL_{}".format(
            datetime.datetime.now().strftime("%d-%m-%y"))
        worksheet = workbook.add_worksheet(name=title)

        worksheet.write('A1', 'Resource ID', heading)
        worksheet.write('B1', 'Resource Name', heading)
        worksheet.write('C1', 'Type', heading)
        worksheet.write('D1', 'Linguality', heading)
        worksheet.write('E1', 'Language(s)', heading)
        worksheet.write_comment('E1', 'Delimited by "|" as per language')
        worksheet.write('F1', 'Resource Size', heading)
        worksheet.write_comment('F1', 'Delimited by "|" as per size')
        worksheet.write('G1', 'Resource Size Unit(s)', heading)
        worksheet.write('H1', 'Domain(s)', heading)
        worksheet.write('I1', 'DSI Relevance', heading)
        worksheet.write('J1', 'Legal Status', heading)
        worksheet.write('K1', 'Countries', heading)

        link = True

        j = 1
        for i in range(len(unique_resources)):

            res = unique_resources[i]
            country = _get_country(res)
            licences = []
            try:
                for dist in res.distributioninfotype_model_set.all():
                    for licence_info in dist.licenceInfo.all():
                        licences.append(licence_info.licence)
            except:
                licences.append("underReview")
            try:
                res_name = smart_str(res.identificationInfo.resourceName['en'])
            except KeyError:
                res_name = smart_str(res.identificationInfo.resourceName[res.identificationInfo.resourceName.keys()[0]])

            # date
            date = datetime.datetime.strptime(unicode(res.storage_object.created).split(" ")[0], "%Y-%m-%d")

            # A1
            worksheet.write(j, 0, res.id)
            # B1
            worksheet.write(j, 1, res_name.decode('utf-8'), bold)
            # C1
            worksheet.write(j, 2, res.resource_type())
            # D1
            linguality = _get_resource_linguality(res)
            worksheet.write(j, 3, ", ".join(linguality))
            # E1
            lang_info = _get_resource_lang_info(res)
            size_info = _get_resource_sizes(res)
            langs = []
            for l in lang_info:
                langs.append(l)
            worksheet.write(j, 4, " | ".join(langs))
            # F1, G1
            preferred_size = _get_preferred_size(res)
            if preferred_size:
                if float(preferred_size.size).is_integer():
                    size_num = int(preferred_size.size)
                else:
                    size_num = float(preferred_size.size)
                worksheet.write_number(j, 5, size_num)
                worksheet.write(j, 6, prettify_camel_case_string(preferred_size.sizeUnit))
            else:
                worksheet.write(j, 5, "")
                worksheet.write(j, 6, "")
            # H1
            domain_info = _get_resource_domain_info(res)
            if domain_info:
                domains = []
                for d in domain_info:
                    domains.append(d)
                worksheet.write(j, 7, " | ".join(domains))
            else:
                worksheet.write(j, 7, "N/A")
            # I1
            dsis = "N/A"
            if res.identificationInfo.appropriatenessForDSI:
                dsis = ", ".join(res.identificationInfo.appropriatenessForDSI)
            worksheet.write(j, 8, dsis)
            # J1
            worksheet.write(j, 9, ", ".join(licences))
            # K1
            if country:
                worksheet.write(j, 10, country)
            else:
                worksheet.write(j, 10, "N/A")

            j += 1
            # worksheet.write(i + 1, 3, _get_resource_size_info(res))
        # worksheet.write(len(resources)+2, 3, "Total Resources", bold)
        # worksheet.write_number(len(resources)+3, 3, len(resources))
        worksheet.freeze_panes(1, 0)
        workbook.close()

        # Send email
        msg_body = "Dear all,\n" \
                   "Please find attached an overview of the resources available in the ELRC-SHARE " \
                   "repository and their status today, {}.\n" \
                   "Best regards,\n\n" \
                   "The ELRC-SHARE group".format(datetime.datetime.now().strftime("%d, %b %Y"))
        msg = EmailMessage("[ELRC] ERLC-SHARE CEF-Digital report", msg_body,
                           from_email='elrc-share@ilsp.gr', to=ILSP_ADMINS)
        msg.attach("{}.xlsx".format(title), output.getvalue(),
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        msg.send()
        return HttpResponse("{}: CEF Digital repository report sent to: {}\n"
                            .format(datetime.datetime.now().strftime("%a, %d %b %Y"), ", ".join(ILSP_ADMINS)))


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Creating CEF Digital report\n")
        _cefdigital_report()
