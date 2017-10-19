import requests
import json
import logging

from metashare import settings
from metashare.local_settings import (
    AP_URL, REST_PASSWORD, REST_USERNAME,
    REST_LOGIN_URL, REST_AUTH_URL,
    PMODE_POST_URL, TRUSTSTORE_POST_URL,
    TRUSTSTORE_PASSWORD
)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(settings.LOG_HANDLER)


def update_pmode(pmode_file):
    credentials = {'username': REST_USERNAME, 'password': REST_PASSWORD}
    with open(pmode_file, 'rb') as pmode_input:
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

        result = session.post(PMODE_POST_URL,
                              files={'file': pmode_input},
                              headers=post_headers).content

        LOGGER.info(result)
        session.close()


def update_trustore(truststore_file):
    credentials = {'username': REST_USERNAME, 'password': REST_PASSWORD}
    with open(truststore_file, 'rb') as truststore_input:
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
        print result
        LOGGER.info(result)
        session.close()
