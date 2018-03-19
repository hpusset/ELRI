# -*- coding: utf-8 -*-
"""
   The mimetypes and and labels choices obtained.
"""

from metashare.repository.supermodel import _make_choices_from_list_alt

MIMETYPELABEL_TO_MIMETYPEVALUE = {}
MIMETYPELABEL_TO_MIMETYPEVALUE[u'TEI'] = u"application/tei+xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'text with tab-separated-values'] = u"text/tab-separated-values"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'TEX'] = u"application/x-tex"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'HTML'] = u"text/html"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'TMX'] = u"application/x-tmx+xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'CSV'] = u"text/csv"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'LATEX'] = u"application/x-latex"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'PDF'] = u"application/pdf"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'XMI'] = u"application/vnd.xmi+xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'XML'] = u"application/xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'Term Base eXchange'] = u"application/x-tbx"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'JSON'] = u"application/json"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'SGML'] = u"text/sgml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'MS-Access database'] = u"application/x-msaccess"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'MS-Excel xls'] = u"application/vnd.ms-excel"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'MS-Excel xlsx'] = u"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'MS-Word docx'] = u"application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'MS-Word doc'] = u"application/msword"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'TM format of the SDL alignment tool'] = u'application/x-SDL-TM'
MIMETYPELABEL_TO_MIMETYPEVALUE[u'RDF'] = u"application/rdf+xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'XHTML'] = u"application/xhtml+xml"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'RTF'] = u"application/rtf"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'other'] = u"other"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'Plain text'] = u"text/plain"
MIMETYPELABEL_TO_MIMETYPEVALUE[u'XCES'] = u"application/x-xces+xml"

MIMETYPEVALUE_TO_MIMETYPELABEL = {}
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/xml'] = u"XML"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/json'] = u"JSON"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/tei+xml'] = u"TEI"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/rtf'] = u"RTF"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/vnd.xmi+xml'] = u"XMI"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-latex'] = u"LATEX"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-tmx+xml'] = u"TMX"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-tbx'] = u"Term Base eXchange"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'text/html'] = u"HTML"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'text/sgml'] = u"SGML"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-tex'] = u"TEX"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'other'] = u"other"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'text/plain'] = u"Plain text"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-msaccess'] = u"MS-Access database"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-SDL-TM'] = u'TM format of the SDL alignment tool'
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/pdf'] = u"PDF"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/xhtml+xml'] = u"XHTML"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'text/csv'] = u"CSV"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'text/tab-separated-values'] = u"text with tab-separated-values"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = u"MS-Word docx"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/msword'] = u"MS-Word doc"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/rdf+xml'] = u"RDF"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/x-xces+xml'] = u"XCES"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/vnd.ms-excel'] = u"MS-Excel xls"
MIMETYPEVALUE_TO_MIMETYPELABEL[u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = u"MS-Excel xlsx"

TEXTFORMATINFOTYPE_DATAFORMAT_CHOICES = _make_choices_from_list_alt([
    u'text/plain',
    u'application/vnd.xmi+xml',
    u'application/xml',
    u'application/json',
    u'application/x-tmx+xml',
    u'application/x-xces+xml',
    u'application/tei+xml',
    u'application/rdf+xml',
    u'application/x-tbx',
    u'application/xhtml+xml',
    u'text/sgml',
    u'text/html',
    u'application/x-tex',
    u'application/rtf',
    u'application/x-latex',
    u'text/csv',
    u'text/tab-separated-values',
    u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    u'application/msword',
    u'application/pdf',
    u'application/x-msaccess',
    u'application/x-SDL-TM',
    u'application/vnd.ms-excel',
    u'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    u'other'], MIMETYPEVALUE_TO_MIMETYPELABEL)
