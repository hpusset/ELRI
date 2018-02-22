import subprocess

import jks
from lxml import etree

import requests
import json
import logging

from metashare import settings
from metashare.local_settings import (
    AP_URL, REST_PASSWORD, REST_USERNAME,
    REST_LOGIN_URL, REST_AUTH_URL,
    PMODE_POST_URL, TRUSTSTORE_POST_URL,
    TRUSTSTORE_PASSWORD,
    PMODE_FILE, ADD_COMMAND, TRUSTORE_FILE, REMOVE_COMMAND)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(settings.LOG_HANDLER)


def update_pmode(obj, mode="add"):
    etree.clear_error_log()
    # parse the pmode xml template
    try:
        pmode = etree.parse(PMODE_FILE)

        parties = pmode.find("/businessProcesses/parties")
        init_parties = pmode.find("//initiatorParties")
        party_exists = pmode.xpath("//party[@name='{}']".format(obj.gateway_party_name))
        if not party_exists and mode == 'add':
            new_party = etree.SubElement(parties, 'party',
                                         {
                                             'name': obj.gateway_party_name,
                                             'endpoint': obj.endpoint,
                                             'allowChunking': 'false'
                                         })
            etree.SubElement(new_party, 'identifier',
                             {
                                 'partyId': obj.gateway_party_id,
                                 'partyIdType': 'partyTypeUrn'
                             })
            # add to initiator parties
            etree.SubElement(init_parties, 'initiatorParty', {'name': obj.gateway_party_name})
        else:
            # get party to remove
            for party in parties.xpath(".//party[@name='{}']".format(obj.gateway_party_name)):
                party.getparent().remove(party)
            # also remove from initiatorParties
            for init_party in init_parties.xpath(".//initiatorParty[@name='{}']".format(obj.gateway_party_name)):
                init_party.getparent().remove(init_party)
        # write the reult tree back to xml
        f = open(PMODE_FILE, 'w')
        f.write(etree.tostring(pmode, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        f.close()
    except Exception, e:
        return {'success': False, 'msg': "Could not parse pmode template: {}".format(e.message)}
    # Next we try to update the actual access point pmode using the updated template
    return _update_ap_pmode(PMODE_FILE)


def _update_ap_pmode(pmode_file):
    credentials = {'username': REST_USERNAME, 'password': REST_PASSWORD}
    with open(pmode_file, 'rb') as pmode_input:
        # create a client
        session = requests.Session()
        try:
            # get the CSRF token
            token = session.get(AP_URL).cookies['XSRF-TOKEN']
            headers = {'Content-Type': 'application/json', 'X-XSRF-TOKEN': token,
                       'Referer': REST_LOGIN_URL}
            # login to REST API
            session.post(REST_AUTH_URL, data=json.dumps(credentials), headers=headers)

            post_headers = {'Accept': 'application/json', 'X-XSRF-TOKEN': token,
                            'Referer': REST_AUTH_URL}

            result = session.post(PMODE_POST_URL,
                                  files={'file': pmode_input},
                                  headers=post_headers).content

            LOGGER.info(result)
            session.close()
            return {'success': True, 'msg': result}
        except Exception as ex:
            return {'success': False, 'msg': "Could not update access point PMode: {}".format(ex)}


def _update_ap_trustore(truststore_file):
    credentials = {'username': REST_USERNAME, 'password': REST_PASSWORD}
    with open(truststore_file, 'rb') as truststore_input:
        try:
            # create a client
            session = requests.Session()
            # get the CSRF token
            token = session.get(AP_URL).cookies['XSRF-TOKEN']
            headers = {'Content-Type': 'application/json', 'X-XSRF-TOKEN': token,
                       'Referer': REST_LOGIN_URL}
            # login to REST API
            session.post(REST_AUTH_URL, data=json.dumps(credentials), headers=headers)

            post_headers = {'Accept': 'application/json', 'X-XSRF-TOKEN': token,
                            'Referer': REST_AUTH_URL}

            result = session.post(TRUSTSTORE_POST_URL,
                                  files={'truststore': truststore_input},
                                  headers=post_headers,
                                  data={'password': TRUSTSTORE_PASSWORD}, ).content
            LOGGER.info(result)
            session.close()
            return {'success': True, 'msg': result}
        except Exception as ex:
            return {'success': False, 'msg': "Could not update access point trustore: {}".format(ex)}


def update_truststore(alias, certificate=None, mode="add"):
    # Using subprocess
    # TODO: Secure that
    if mode == "add":
        c = ADD_COMMAND.format(alias, TRUSTSTORE_PASSWORD, certificate, TRUSTORE_FILE)
    else:
        c = REMOVE_COMMAND.format(alias, TRUSTORE_FILE, TRUSTSTORE_PASSWORD)
    subprocess.call(c, shell=True)
    # verify that cert is inserted
    ks = jks.KeyStore.load(TRUSTORE_FILE, TRUSTSTORE_PASSWORD)

    if mode is not "add":
        if alias not in ks.entries.keys():
            return _update_ap_trustore(TRUSTORE_FILE)
    else:
        if alias in ks.entries.keys():
            return _update_ap_trustore(TRUSTORE_FILE)

    return {'success': False, 'msg': "Could not update local trustore."}
