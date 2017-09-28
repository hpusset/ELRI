from metashare.repository.models import resourceInfoType_model as rm, corpusInfoType_model, \
    lexicalConceptualResourceInfoType_model, languageDescriptionInfoType_model
from metashare.utils import prettify_camel_case_string

all_resources = rm.objects.all()


def count_by_domain():
    domains = ["BUSINESS & COMPETITION", "INTERNATIONAL RELATIONS", "EDUCATION & COMMUNICATIONS",
               "PRODUCTION, TECHNOLOGY & RESEARCH", "LAW", "POLITICS", "EMPLOYMENT & WORKING CONDITIONS",
               "EUROPEAN UNION", "SOCIAL QUESTIONS", "FINANCE", "TRANSPORT", "ECONOMICS", "INDUSTRY",
               "AGRICULTURE, FORESTRY & FISHERIES", "GEOGRAPHY", "Other", "SCIENCE", "TRADE", "ENVIRONMENT",
               "AGRI-FOODSTUFFS", "INTERNATIONAL ORGANISATIONS", "ENERGY"]
    resources = []
    result = []
    for r in all_resources:
        is_relations = [rel.relationType.startswith("is") for rel in r.relationinfotype_model_set.all()]
        status = r.storage_object.publication_status
        if status == 'p' or (status=='g' and any(is_relations)):
            resources.append(r)
    for d in domains:
        count = 0
        for res in resources:
            if d in _get_resource_domain_info(res):
                count += 1
        result.append((d, count))
    return result


def _get_resource_domain_info(resource):
    result = []
    media = resource.resourceComponentType.as_subclass()

    if isinstance(media, corpusInfoType_model):
        media_type = media.corpusMediaType
        for corpus_info in media_type.corpustextinfotype_model_set.all():
            result.extend([prettify_camel_case_string(d.domain)
                           if d.subdomain else prettify_camel_case_string(d.domain) for d in
                           corpus_info.domaininfotype_model_set.all()])

    elif isinstance(media, lexicalConceptualResourceInfoType_model):
        lcr_media_type = media.lexicalConceptualResourceMediaType
        if lcr_media_type.lexicalConceptualResourceTextInfo:
            result.extend([prettify_camel_case_string(d.domain)
                           if d.subdomain else prettify_camel_case_string(d.domain) for d in lcr_media_type \
                          .lexicalConceptualResourceTextInfo.domaininfotype_model_set.all()])

    elif isinstance(media, languageDescriptionInfoType_model):
        ld_media_type = media.languageDescriptionMediaType
        if ld_media_type.languageDescriptionTextInfo:
            result.extend([prettify_camel_case_string(d.domain)
                           if d.subdomain else prettify_camel_case_string(d.domain) for d in ld_media_type \
                          .languageDescriptionTextInfo.domaininfotype_model_set.all()])
    result = list(set(result))
    result.sort()

    return result