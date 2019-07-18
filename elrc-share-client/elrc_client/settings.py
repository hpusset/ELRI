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

import logging

import os

# import local_settings

TEST_MODE = True

if TEST_MODE:
    REPO_URL = 'http://127.0.0.1:8001'  # dev url
else:
    REPO_URL = 'https://elrc-share.eu'
LOGIN_URL = '%s/login/' % REPO_URL
LOGOUT_URL = '%s/logout/' % REPO_URL
API_ENDPOINT = '%s/repository/api/editor/lr/' % REPO_URL
API_OPERATIONS = '%s/repository/api/operations/' % REPO_URL
XML_UPLOAD_URL = '%s/repository/api/create/' % REPO_URL
XML_SCHEMA = 'https://elrc-share.eu/ELRC-SHARE_SCHEMA/v2.0/ELRC-SHARE-Resource.xsd'

# Set default directory for downloads
if os.name == 'posix':
    DOWNLOAD_DIR = '/home/{}/ELRC-Downloads'.format(os.getlogin())
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
elif os.name == 'nt':
    DOWNLOAD_DIR = 'C:\\Users\\{}\\Downloads\\ELRC-Downloads'.format(os.getlogin())

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] ELRC-SHARE::%(levelname)-5.5s  %(message)s",
    handlers=[
        logging.StreamHandler()
    ])
