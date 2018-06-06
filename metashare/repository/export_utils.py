import xmltodict
import json
from collections import OrderedDict
from metashare.xml_utils import to_xml_string


def xml_to_json(obj):
    list_fields = ['distributionInfo', 'licenceInfo', 'corpusTextInfo',
                   'distributionMedium', 'downloadLocation', 'executionLocation',
                   'attributionText', 'iprHolder', 'contactPerson', 'surname']

    # get xml representation
    xml_string = to_xml_string(obj.export_to_elementtree(), encoding="utf-8").encode("utf-8")

    # parse xml to dict
    dict_repr = xmltodict.parse(xml_string, force_list=list_fields)
    return json.dumps(dict_repr, indent=4).encode('utf8')


def json_to_xml(json_string):
    print json.loads(json_string, object_pairs_hook=OrderedDict)
    return xmltodict.unparse(json.loads(json_string, object_pairs_hook=OrderedDict), pretty=True).encode('utf-8')
