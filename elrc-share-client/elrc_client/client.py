# ELRC-SHARE-client API source code BSD-3-clause licence
#
# Copyright (c) 2019
#
# This software has been developed by the Institute for Language and
# Speech Processing/Athena Research Centre as part of Service
# Contract 30-CE-0816330/00-16 for the European Union represented by
# the European Commission.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import atexit
import json
import zipfile

import os

import requests
import httplib
from elrc_client.settings import LOGIN_URL, API_ENDPOINT, LOGOUT_URL, API_OPERATIONS, DOWNLOAD_DIR
from elrc_client.settings import logging
from elrc_client.utils.util import is_xml
from elrc_client.utils.xml import parser


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict, ensure_ascii=False))


class ELRCShareClient:
    def __init__(self):
        self.session = None
        self.csrftoken = None
        self.user_log_in = None
        self.logged_in = False
        self.headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://www.elrc-share.eu/'
        }

        atexit.register(self.logout)

    def login(self, username, password):
        try:
            self.session = requests.session()
            self.user_log_in = self.session.get(LOGIN_URL)
            self.csrftoken = self.session.cookies['csrftoken']
            if self.user_log_in.ok:
                login_data = {
                    'username': username,
                    'password': password,
                    'csrfmiddlewaretoken': self.csrftoken
                }
                # Login to site
                try:
                    login = self.session.post(LOGIN_URL, data=login_data,
                                              headers={'referer': 'https://elrc-share.eu/'})
                    if 'Your username and password didn\'t match' in login.text or login.status_code != httplib.OK:
                        logging.error('Unsuccessful Login...')
                    else:
                        self.logged_in = True
                        logging.info('Login Successful!')
                except requests.exceptions.ConnectionError:
                    logging.error('Could not connect to remote host.')
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def logout(self):
        """
        Logout user and close session when program exits
        """
        if self.logged_in:
            try:
                self.session.get(LOGOUT_URL)
                self.session.close()
                self.logged_in = False
                logging.info("Logout....")
            except requests.exceptions.ConnectionError:
                logging.error('Could not connect to remote host.')
        else:
            pass

    def _create_resource(self, description, dataset=None):

        # reset headers
        self.headers = {
            'Content-Type': 'application/json'
        }

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return None

        if description.get('resourceInfo').get('resourceComponentType').get('toolServiceInfo'):
            # Tool/Service not supported
            logging.error("Tool/Services are not yet supported")
            return None

        resource_name = description.get('resourceInfo').get('identificationInfo').get('resourceName').get('en')
        # print(json.dumps(description, ensure_ascii=False))
        try:
            request = self.session.post(API_ENDPOINT, headers=self.headers,
                                        data=json.dumps(description, ensure_ascii=False).encode('utf-8'))

            if request.status_code == httplib.CREATED:
                print("Metadata created")
                new_id = json.loads(request.content).get('ID')
                print("Resource '{}' has been created\nID: {}".format(resource_name, new_id))
                try:
                    self.upload_data(new_id, data_file=dataset)
                except Exception as e:
                    pass
                return new_id
            elif request.status_code == httplib.UNAUTHORIZED:
                logging.error('401 Unauthorized Request')
            else:
                logging.error('{} Could not create resource'.format(request.status_code))
                logging.error(request.text)
        except requests.exceptions.ConnectionError:
            logging.error('Could not connect to remote host.')

    def create(self, file, dataset=None):
        """
        Create one or more resources on ELRC-SHARE repository.
        :param file: Path to resource description xml file or a directory containing xml descriptions
        :param dataset: Optional path to associated dataset (used for single resource creation)
        :return:
        """
        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return
        if os.path.isdir(file):
            for f in os.listdir(file):
                data = None
                if is_xml(f):
                    logging.info('Processing file: {}'.format(f))
                    with open(os.path.join(file, f), 'r') as inp:
                        data = parser.parse(inp.read())
                    attached_dataset = os.path.join(file, f.replace('.xml', '.zip'))
                    if zipfile.is_zipfile(attached_dataset):
                        logging.info('Dataset {} found'.format(attached_dataset))
                        self._create_resource(data, dataset=attached_dataset)
                    else:
                        logging.info('No dataset found for this resource'.format(attached_dataset))
                        self._create_resource(data)
        else:
            logging.info('Processing file: {}'.format(file))
            with open(os.path.join(os.path.dirname(__file__), file), 'r') as f:
                data = parser.parse(f.read())
            return self._create_resource(data, dataset=dataset)

    def upload_data(self, resource_id, data_file):
        """
        Upload a .zip dataset for the given resource
        :param resource_id: ELRC-SHARE resource id
        :param data_file: Path to the .zip file to be uploaded
        """

        # reset headers
        self.headers = {
            'Content-Type': 'application/json'
        }

        if not self.logged_in:
            logging.error("Please login to ELRC-SHARE using your credentials")
            return

        # determine dataset by resource filename
        if not zipfile.is_zipfile(data_file):
            logging.error('Not a valid zip archive')
            return
        else:
            try:
                del self.headers['Content-Type']
            except KeyError:
                pass
            self.headers.update({'X-CSRFToken': self.session.cookies['csrftoken']})
            url = "{}upload_data/{}/".format(API_OPERATIONS, resource_id)
            data = {
                'csrfmiddlewaretoken': self.session.cookies['csrftoken'],
                'uploadTerms': 'on',
                'api': True}

            print('Uploading dataset {} ({:,.2f}Mb)'.format(data_file, os.path.getsize(data_file) / (1024 * 1024.0)))

            response = self.session.post(url, files={'resource': open(data_file, 'rb')}, data=data)
            if response.status_code is not 200:
                logging.error("Could not upload dataset for the given resource id ({})".format(resource_id))
            else:
                print(response.text)

