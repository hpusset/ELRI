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

import sys

import os
from elrc_client.settings import XML_SCHEMA
from io import StringIO
from lxml import etree


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def parse_xml_well_formed(xml_string):
    # parse xml
    try:
        doc = etree.parse(StringIO(xml_string))
        print('XML well formed, syntax ok.')
        return doc
    # check for file IO error
    except IOError:
        print('Invalid File')
        return False
    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        print('XML Syntax Error, see error_syntax.log')
        return False
    except:
        print('Unknown error, exiting.')
        return False


def validate(xml_file):
    xml = open(xml_file, 'r', encoding='utf-8').read()
    print(XML_SCHEMA)
    xmlschema_doc = etree.parse(StringIO(XML_SCHEMA))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = parse_xml_well_formed(xml)
    if doc:
        # validate against schema
        try:
            xmlschema.assertValid(doc)
            print('XML valid, schema validation ok.')
            return True
        except etree.DocumentInvalid as err:
            print('Schema validation error, see error_schema.log')
            return False
        except:
            print('Unknown error, exiting.')
            return False


def is_xml(f):
    return f.endswith('.xml')


class ChunkUploader(object):
    def __init__(self, filename, session, url, chunksize=1 << 13):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.readsofar = 0
        self.url = session
        self.session = url

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    sys.stderr.write("\n")
                    break
                self.session.post(self.url, files={'resource': file})
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                sys.stderr.write("\r{percent} / {total}".format(percent=self.readsofar, total=self.totalsize))
                yield data

    def __len__(self):
        return self.totalsize
