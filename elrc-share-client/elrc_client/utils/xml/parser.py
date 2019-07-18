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

import xmltodict
from collections import OrderedDict

try:
    from defusedexpat import pyexpat as expat
except ImportError:
    from xml.parsers import expat


class Parser(xmltodict._DictSAXHandler):
    def __init__(self,
                 item_depth=0,
                 item_callback=lambda *args: True,
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=False,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True,
                 namespace_separator=':',
                 namespaces=None,
                 force_list=None):
        self.path = []
        self.stack = []
        self.data = []
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace
        self.namespace_separator = namespace_separator
        self.namespaces = namespaces
        self.namespace_declarations = OrderedDict()
        self.force_list = force_list
        self.attrs = dict()

    def _attrs_to_dict(self, attrs):
        if isinstance(attrs, dict):
            return attrs
        return self.dict_constructor(zip(attrs[0::2], attrs[1::2]))

    def startElement(self, full_name, attrs):
        name = self._build_name(full_name)
        self.attrs = self._attrs_to_dict(attrs)
        if self.attrs and self.namespace_declarations:
            self.attrs['xmlns'] = self.namespace_declarations
            self.namespace_declarations = OrderedDict()
        self.path.append((name, self.attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attr_entries = []
                entry = dict()
                for key, value in self.attrs.items():
                    if key not in ['xmlns', 'xmlns:xsi', 'xsi:schemaLocation']:
                        key = self.attr_prefix + self._build_name(key)
                        # if self.postprocessor:
                        #     entry = self.postprocessor(self.path, key, value)

                        entry.update({key: value})
                attr_entries.append(entry)
                self.attrs = entry
            else:
                self.attrs = None
            self.item = self.attrs or None
            self.data = []

    def endElement(self, full_name):
        name = self._build_name(full_name)
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = (None if not self.data
                        else self.cdata_separator.join(self.data))
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise xmltodict.ParsingInterrupted()
        if len(self.stack):
            data = (None if not self.data
                    else self.cdata_separator.join(self.data))
            item = self.item
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    if self.attrs:
                        self.push_data(item, self.attrs['@lang'], data)
                        del self.attrs['@lang']
                    else:
                        self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                if data == 'true':
                    data = bool('true')
                elif data == 'false':
                    data = False
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = None
            self.data = []
        self.path.pop()

    def push_data(self, item, key, data, raw=False):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            elif isinstance(value, dict):
                value.update(data)
            else:
                item[key] = [value, data]
        except KeyError:
            if self._should_force_list(key, data):
                item[key] = [data]
            else:
                item[key] = data
        return item


def parse(xml_input, encoding=None, expat=expat, process_namespaces=False,
          namespace_separator=':', disable_entities=True, **kwargs):
    force_list = [
        'domainSetInfo', 'evaluationCriteria', 'inputInfoType_model.resourceType', 'relationInfo',
        'domainSetInfo.domainId', 'annotationInfo', 'validationInfo', 'textClassificationInfo',
        'telephoneNumber', 'requiredLRs', 'annotationManual', 'metadataLanguageName', 'appropriatenessForDSI',
        'evaluationTool', 'operatingSystem', 'metadataLanguageId', 'originalSource', 'documentation',
        'segmentationLevel', 'encodingLevel', 'variant', 'fundingCountryId', 'funder', 'languageSetInfo',
        'inputInfoType_model.annotationType', 'outputInfoType_model.annotationType',
        'affiliation', 'fundingType', 'validator', 'identifier', 'theoreticModel',
        'creationTool', 'distributionInfo', 'licenceInfo', 'evaluationLevel', 'sizePerLanguage',
        'languageVarietyName', 'restrictionsOfUse', 'domainSetInfo.domain', 'contactPerson',
        'evaluationReport', 'outputInfoType_model.resourceType', 'domainSetInfo.subdomainId', 'evaluationMeasure',
        'keywords', 'fundingCountry', 'url', 'author', 'iprHolder', 'annotationTool', 'email',
        'requiredSoftware', 'domainInfo', 'languageVarietyInfo', 'conformanceToStandardsBestPractices',
        'characterEncodingInfo', 'extratextualInformation', 'textFormatInfo', 'distributionMedium',
        'corpusTextInfo', 'implementationLanguage', 'publisher', 'externalRef', 'languageInfo',
        'resourceCreator', 'evaluator', 'executionLocation', 'domainSetInfo.subdomain', 'samplesLocation',
        'linguisticInformation', 'function', 'fundingProject', 'downloadLocation', 'sizeInfo', 'editor',
        'task', 'extraTextualInformationUnit', 'metadataCreator', 'validationReport',
        'outputInfoType_model.mediaType'
    ]

    handler = Parser(namespace_separator=namespace_separator, force_list=force_list,
                     **kwargs)
    if isinstance(xml_input, xmltodict._unicode):
        if not encoding:
            encoding = 'utf-8'
        xml_input = xml_input.encode(encoding)
    if not process_namespaces:
        namespace_separator = None
    parser = expat.ParserCreate(
        encoding,
        namespace_separator
    )
    try:
        parser.ordered_attributes = True
    except AttributeError:
        # Jython's expat does not support ordered_attributes
        pass
    parser.StartNamespaceDeclHandler = handler.startNamespaceDecl
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    parser.buffer_text = True
    if disable_entities:
        try:
            # Attempt to disable DTD in Jython's expat parser (Xerces-J).
            feature = "http://apache.org/xml/features/disallow-doctype-decl"
            parser._reader.setFeature(feature, True)
        except AttributeError:
            # For CPython / expat parser.
            # Anything not handled ends up here and entities aren't expanded.
            parser.DefaultHandler = lambda x: None
            # Expects an integer return; zero means failure -> expat.ExpatError.
            parser.ExternalEntityRefHandler = lambda *x: 1
    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item
