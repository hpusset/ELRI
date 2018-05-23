import json

import datetime

from metashare.settings import UNIQUE_RESOURCES_SNAPSHOTS
from metashare.report_utils.report_utils import _is_processed, _is_not_processed_or_related, _get_resource_mimetypes, \
    _get_resource_linguality, _get_resource_lang_info, _get_resource_domain_info, get_licenses, _get_country
from metashare.repository import model_utils
from metashare.repository.fields import best_lang_value_retriever
from metashare.repository.models import resourceInfoType_model
from metashare.repository.views import status
from metashare.stats.model_utils import DOWNLOAD_STAT, VIEW_STAT


def _get_psi(r):
    psi_list = [d.PSI for d in r.distributioninfotype_model_set.all()]
    return any(psi_list)


def get_projects(r):
    try:
        rc = r.resourceCreationInfo
        funding_projects = [best_lang_value_retriever(fp.projectShortName) for fp in rc.fundingProject.all()]
    except AttributeError:
        funding_projects = []
    return funding_projects


def get_related_ids(r):
    related_ids = []
    if r.relationinfotype_model_set.all():
        set([rel.relatedResource.targetResourceNameURI
             for rel in r.relationinfotype_model_set.all()])
    return related_ids


def create_snapshot():
    unique_resources = [r for r in resourceInfoType_model.objects.filter(
        storage_object__deleted=False) if (_is_processed(r) or _is_not_processed_or_related(r))]

    # init dict
    json_output = dict(unique_resources={"count": len(unique_resources), "metadata": []})

    for r in unique_resources:
        output = dict()
        output["id"] = r.id
        output['resourceName'] = best_lang_value_retriever(r.identificationInfo.resourceName)
        output['resourceType'] = r.resource_type()
        output['mimetypes'] = _get_resource_mimetypes(r)
        output['linguality'] = _get_resource_linguality(r)
        output['languages'] = list(set(_get_resource_lang_info(r)))
        output['domains'] = list(set(_get_resource_domain_info(r)))
        output['dsis'] = list(set(r.identificationInfo.appropriatenessForDSI))
        output['licences'] = list(set(get_licenses(r)))
        output['psi'] = _get_psi(r)
        output['country'] = _get_country(r)
        output['created'] = r.storage_object.created.strftime("%d-%m-%Y")
        output['downloads'] = model_utils.get_lr_stat_action_count(r.storage_object.identifier, DOWNLOAD_STAT)
        output['views'] = model_utils.get_lr_stat_action_count(r.storage_object.identifier, VIEW_STAT)
        # output['partner'] = r.management_object.partner_responsible
        output['projects'] = get_projects(r)
        # output['processed'] = r.management_object.is_processed_version
        output['related_resources'] = get_related_ids(r)
        output['validated'] = True if r.storage_object.get_validation() else False
        output['status'] = status[r.storage_object.publication_status]

        json_output['unique_resources']['metadata'].append(output)

    out_file_path = "{}/unique_resources_{}.json".format(UNIQUE_RESOURCES_SNAPSHOTS, datetime.datetime.today().strftime("%d-%m-%Y"))
    out_file = open(out_file_path, "w")
    out_file.write(json.dumps(json_output, indent=4, sort_keys=True))
    out_file.close()

    return out_file_path

