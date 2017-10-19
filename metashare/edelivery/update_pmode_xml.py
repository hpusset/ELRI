from lxml import etree

from metashare.local_settings import PMODE_FILE
from .update_ap_files import update_pmode as up_ap

pmode = etree.parse(PMODE_FILE)


def update_pmode_xml(edo):
    # edo = edelivery application object

    parties = pmode.find("/businessProcesses/parties")
    new_party = etree.SubElement(parties, 'party',
                                 {
                                     'name': edo.gateway_party_name,
                                     'endpoint': edo.endpoint,
                                     'allowChunking': 'false'
                                 })
    etree.SubElement(new_party, 'identifier',
                     {
                         'partyId': edo.gateway_party_id,
                         'partyIdType': 'partyTypeUrn'
                     })
    # add to initiator parties
    init_parties = pmode.find("//initiatorParties")
    etree.SubElement(init_parties, 'initiatorParty', {'name': edo.gateway_party_name})
    print etree.tostring(init_parties, pretty_print=True)
    f = open(PMODE_FILE, 'w')
    f.write(etree.tostring(pmode, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
    f.close()

    up_ap(PMODE_FILE)
    # print etree.tostring(parties, pretty_print=True)
