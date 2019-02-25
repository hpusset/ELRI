import pprint
import shutil

from datetime import date, datetime
from django.utils.encoding import smart_str

from metashare.repository.models import resourceInfoType_model, versionInfoType_model, targetResourceInfoType_model, \
    relationInfoType_model, projectInfoType_model
from metashare.settings import DJANGO_URL
from metashare.storage.models import INGESTED, MASTER
from metashare.xml_utils import to_xml_string, import_from_string
from lxml import etree
import os
import zipfile
import fnmatch

pp = pprint.PrettyPrinter(indent=4)

PWD = os.path.dirname(__file__)
INPUT_DIR = os.path.join(PWD, "input")
OUTPUT_DIR = os.path.join(PWD, "output")

NS = {"ms": "http://www.elrc-share.eu/ELRC-SHARE_SCHEMA/v2.0/"}
ns = "{http://www.elrc-share.eu/ELRC-SHARE_SCHEMA/v2.0/}"

data_Format = {
    "TMX": u"application/x-tmx+xml",
    "TBX": u"application/x-tbx",
    "TXT": u"text/plain"
}

relations_map = {
    "TMX": (u"isAlignedVersionOf", u"hasAlignedVersion"),
    "TBX": (u"isConvertedVersionOf", u"hasConvertedVersion"),
    "TXT": (u"isConvertedVersionOf", u"hasConvertedVersion")
}


# One off project creation for all
def get_or_create_project():
    for p in projectInfoType_model.objects.all():
        # first check if the LOT3 project already exists and return that
        if len(p.projectShortName) > 0 and p.projectShortName[u"en"] == u"ELRC Data":
            print "project {} found".format(p)
            return p

    fp = projectInfoType_model.objects.create()
    fp.projectName["en"] = u"European Language Resources Coordination LOT3"
    fp.projectShortName["en"] = u"ELRC Data"
    fp.projectID = u"Tools and Resources for CEF Automated Translation - " \
                   u"LOT3 (SMART 2015/1091 - 30-CE-0816766/00-92)"
    fp.url = [u"http://www.lr-coordination.eu", ]
    fp.fundingType = [u"serviceContract", ]
    fp.funder = [u"European Commission", ]
    fp.fundingCountry = [u"European Union", ]
    fp.projectStartDate = datetime.strptime(u"2016-12-13", u"%Y-%m-%d").date()
    fp.projectEndDate = datetime.strptime(u"2020-02-12", u"%Y-%m-%d").date()
    fp.save()
    return fp


def extract_zip(zip_file_name):
    """
    Extract a zip file to specified directory
    and return the directory path
    """

    # how should I name the extracted directory?
    # e.g. 245.zip --> 245
    output_dir_name = zip_file_name.split(".")[0]
    target_directory = os.path.join(OUTPUT_DIR, output_dir_name)
    # if the directory does not exist, make it
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # red the zip file and extract it
    zip_file = zipfile.ZipFile(os.path.join(INPUT_DIR, zip_file_name))
    zip_file.extractall(target_directory)
    zip_file.close()

    return {
        "path": os.path.abspath(target_directory),
        "directory": int(output_dir_name)
    }


def count_tus(tmx_file):
    tmx = etree.parse(tmx_file)
    count = tmx.xpath(u"count(//tu)")
    return count


def count_terms(tbx_file):
    tmx = etree.parse(tbx_file)
    count = tmx.xpath(u"count(//termEntry)")
    return count


def prepare_dir(d, in_dir):
    mimetype = ""
    file_count = 0
    sizes = list()
    relation = {}
    if os.path.isdir(in_dir):
        zipped = zipfile.ZipFile(os.path.join(in_dir, "archive.zip"), "w")

        # first run to determine mimetype and file count
        for f in os.listdir(in_dir):
            if f.endswith(".tmx"):
                mimetype = "TMX"
                file_count = len(fnmatch.filter(os.listdir(in_dir), '*.tmx'))
                relation["this"] = "isAlignedVersionOf"
                relation["source"] = "hasAlignedVersion"
                break
            elif f.endswith(".txt"):
                mimetype = "TXT"
                file_count = len(fnmatch.filter(os.listdir(in_dir), '*.txt'))
                relation["this"] = "isConvertedVersionOf"
                relation["source"] = "hasConvertedVersion"
                break
            elif "tbx" in f:
                mimetype = "TBX"
                file_count = len(fnmatch.filter(os.listdir(in_dir), '*.tbx*'))
                relation["this"] = "isConvertedVersionOf"
                relation["source"] = "hasConvertedVersion"
                break

        for f in os.listdir(in_dir):
            filepath = os.path.join(in_dir, f)
            if f.endswith(".pdf"):
                try:
                    shutil.move(filepath, os.path.join(in_dir, build_val_rep_name(d)))
                except:
                    pass
            elif not f.endswith(".zip"):
                if f.endswith(".tmx"):
                    sizes.append(int(count_tus(filepath)))
                elif "tbx" in f:
                    sizes.append(int(count_terms(filepath)))
                zipped.write(filepath, os.path.basename(filepath))
                os.remove(filepath)
        zipped.close()

        return {
            "path": os.path.abspath(in_dir),
            "resource_id": int(d),
            "resource_info": extract_source_resource_metadata(int(d)),
            "mimetype": mimetype,
            "relation": relation,
            "size_info": {
                "files": file_count,
                "sizes": sizes,
                "size_sum": int(sum(sizes))
            }
        }


def prepare_input():
    directories = list()
    for d in os.listdir(INPUT_DIR):
        in_dir = os.path.join(INPUT_DIR, d)
        directories.append(prepare_dir(d, in_dir))
    return directories


def build_val_rep_name(target_res_id):
    #name = "ELRC_VALREP_{}_v2.0.pdf".format(target_res_id)
    name = "ELRI_VALREP_{}_v2.0.pdf".format(target_res_id)
    return name


def process_output(output_dir):
    zipped = zipfile.ZipFile(os.path.join(output_dir, "archive.zip"), "w")
    for f in os.listdir(output_dir):
        if f.endswith(".pdf"):
            os.rename(os.path.join(output_dir, f),
                      os.path.join(output_dir, build_val_rep_name(567)))
        elif f.endswith(".tmx"):
            zipped.write(os.path.join(output_dir, f),
                         os.path.basename(os.path.join(output_dir, f)))
    zipped.close()


def extract_source_resource_metadata(res_id):
    res = resourceInfoType_model.objects.get(id=res_id)
    res_owners = res.owners.all()
    view_path = res.get_absolute_url()
    try:
        root_node = res.export_to_elementtree()
        xml_string = to_xml_string(root_node, encoding="utf-8").encode('utf-8')
        return {
            "resource": res,
            "uri": "{}{}".format(DJANGO_URL, view_path),
            "owners": res_owners,
            "metadata": xml_string,
        }

    except:
        print "Could not import resource with id {}: \"{}\"".format(res_id, res)


def create_size_element(unit, size):
    si = etree.Element("sizeInfo")
    sze = etree.SubElement(si, "size")
    sze_unit = etree.SubElement(si, "sizeUnit")
    sze.text = str(size)
    sze_unit.text = unit

    return si


def create_data_format_element(dformat):
    tf = etree.Element("textFormatInfo")
    df = etree.SubElement(tf, "dataFormat")
    df.text = dformat

    return tf


def create_relation_element(relation, target_resource):
    ri = etree.Element("relationInfo")
    rt = etree.SubElement(ri, "relationType")
    rr = etree.SubElement(ri, "relatedResource")
    target = etree.SubElement(rr, "targetResourceNameURI")
    rt.text = relation
    target.text = target_resource

    return ri


def create_version_element(version):
    vi = etree.Element("versionInfo")
    v = etree.SubElement(vi, "version")
    v.text = version

    return vi


def get_info_from_tmx(tmx_file):
    pass


def build_target_metadata(data_dict):
    xml = etree.fromstring(data_dict.get("resource_info").get("metadata"))
    #
    # # PROCESS NAME
    resourceName = xml.find("{}identificationInfo/{}resourceName[@lang='en']".format(ns, ns), namespaces=NS)
    add_to_name = u"(Processed)"
    resourceName.text = u"{} {}".format(resourceName.text, add_to_name)
    print "Adding {} with source id{}".format(smart_str(resourceName.text), data_dict.get("resource_id"))
    #
    # # PROCESS DESCRIPTION
    description = xml.find("{}identificationInfo/{}description[@lang='en']".format(ns, ns), namespaces=NS)
    add_to_descr = u"(Processed)"
    description.text = u"{} {}".format(description.text, add_to_descr)
    #
    # # EDIT TEXTFORMAT
    textformats = xml.findall(".//{}textFormatInfo".format(ns), namespaces=NS)
    for tf in textformats:
        tf.getparent().remove(tf)
    last_size_info = xml.xpath(u'//ms:sizeInfo[last()]', namespaces=NS)
    last_size_info[0].addnext(create_data_format_element(data_Format.get(data_dict.get("mimetype"))))
    #
    # get the languageInfo to append after it

    languageInfo = xml.xpath(u'//ms:languageInfo[last()]', namespaces=NS)
    # sizes

    # HANDLE SIZES
    # delete existing sizes and sizePerLanguage only if processed is TMX
    if data_dict.get("mimetype") is "TMX" or data_dict.get("mimetype") is "TBX":
        size_infos = xml.findall(".//{}sizeInfo".format(ns), namespaces=NS)
        size_per_lang = xml.findall(".//{}sizePerLanguage".format(ns), namespaces=NS)
        for sin in size_infos:
            sin.getparent().remove(sin)
        for spl in size_per_lang:
            spl.getparent().remove(spl)

    try:
        size_info = data_dict["size_info"]
        if size_info["files"] > 1:
            languageInfo[0].addnext(create_size_element("files", size_info["files"]))
        if (data_dict["mimetype"] == 'TMX' or data_dict["mimetype"] == 'TBX') and size_info["size_sum"] > 0:
            languageInfo[0].addnext(create_size_element(
                "translationUnits"
                if data_dict["mimetype"] == 'TMX' else "terms", size_info["size_sum"]))

    except KeyError:
        pass

    # HANDLE RELATIONS AND VERSIONS
    # For each new resource, add the proper relation and version to that resource and its source

    # Processed resource
    # find the last resourceCreationInfo to add relation after it
    resourceCreationInfo = xml.xpath(u'//ms:resourceCreationInfo[last()]', namespaces=NS)

    # create a relation according to the mimetype of the new resource
    relation = create_relation_element(relations_map.get(data_dict.get("mimetype"))[0],
                                       str(data_dict.get("resource_id")))

    # REMEMBER TO ADD THE OPPOSITE RELATION TO SOURCE RESOURCE AFTER IMPORT/SAVE
    resourceCreationInfo[0].addnext(relation)

    # create a version element after metadataInfo
    # <versionInfo>
    #     < version>2.0</version>
    # </versionInfo>

    metadataInfo = resourceCreationInfo = xml.xpath(u'//ms:metadataInfo[last()]', namespaces=NS)
    metadataInfo[0].addnext(create_version_element(u"2.0"))

    # metadataCreationDate=date.today()
    # edit the dates
    updated = metadataInfo[0].find("{}metadataLastDateUpdated".format(ns), namespaces=NS)
    # remove the lastupdated since it's a new record
    updated.getparent().remove(updated)

    # print etree.tostring(xml)
    # create the new record
    new_resource = import_from_string(etree.tostring(xml), INGESTED, MASTER)
    # now add the owners we got from source resoource
    new_resource.owners = data_dict.get("resource_info").get("owners")
    # edit the creation in metadatainfo
    new_resource.metadataInfo.metadataCreationDate = date.today()
    new_resource.metadataInfo.save()

    new_resource.resourceCreationInfo.fundingProject.add(get_or_create_project())
    new_resource.save()

    # and finally "upload" the dataset and validation report to the respective folder
    for ftomove in os.listdir(data_dict.get("path")):
        shutil.move(os.path.join(data_dict.get("path"), ftomove),
                    os.path.join(new_resource.storage_object._storage_folder(), ftomove))
    shutil.rmtree(data_dict.get("path"))

    # MODIFY SOURCE RESOURCE

    source = data_dict.get("resource_info").get("resource")
    source.versionInfo = versionInfoType_model.objects.create(version=u"1.0")
    target_resource = targetResourceInfoType_model.objects.create(targetResourceNameURI=str(new_resource.id))
    source_relation = relationInfoType_model.objects.create(
        relationType=relations_map.get(data_dict.get("mimetype"))[1],
        relatedResource=target_resource)
    source_relation.back_to_resourceinfotype_model = source
    source_relation.save()
    source.save()
    # TODO: ADD opposite relation to source


    # print etree.tostring(xml)


def process():
    print "Preparing directories..."
    directories = prepare_input()

    for item in directories:
        build_target_metadata(item)

        # for f in os.listdir(INPUT_DIR):
        #     # extract the zip file and get initial information
        #     # id of source resource and path to output of extraction
        #     info = extract_zip(f)
        #
        #     info["resource_object"] = extract_source_resource_metadata(info.get('directory'))
        #     pp.pprint(info)
        #     # build_target_metadata(info.get("resource_object").get("metadata"))
