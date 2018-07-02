from metashare.bcp47.iana import get_language_by_subtag
from metashare.eurovoc.eurovoc import get_domain_by_id

haystack_filters = {
    "filters": {
        "language": "languageName",
        "lang": "languageName", "textGenre": "textTextGenre", "textType": "textTextType",
        "conditionOfUse": "restrictionsOfUse", "linguality": "lingualityType", "multilinguality": "multilingualityType",
        "mimetype": "dataFormat", "dsi": "appropriatenessForDSI", "status": "publicationStatus"
    },
    "conditionOfUse": {
        "by": "Attribution", "cu": "Commercial Use", "comp": "Compensate", "edu": "Education",
        "nd": "No Derivatives", "nc": "Non Commercial Use", "res": "Research", "sa": "Share Alike",
    },
    "dsi": {
        "eessi": "Electronic Exchange Of Social Security Information",
        "bris": "Business Registers Interconnection System",
        "cs": "Cybersecurity", "odr": "Online Dispute Resolution", "odp": "Open Data Portal",
        "eh": "E Health", "ej": "E Justice", "ep": "E Procurement", "si": "Safer Internet"
    },
    "linguality": {
        "bi": "Bilingual", "multi": "Multilingual", "mono": "Monolingual"
    },
    "mimetype": {
        "csv": "CSV", "html": "HTML", "json": "JSON", "latex": "LATEX", "accessdb": "MS-Access database",
        "xls": "MS-Excel xls", "xlsx": "MS-Excel xlsx", "doc": "MS-Word doc", "docx": "MS-Word docx",
        "pdf": "PDF", "txt": "Plain text", "rdf": "RDF", "rtf": "RTF", "sgml": "SGML", "tei": "TEI",
        "tex": "TEX", "tsv": "text with tab-separated-values", "sdl": "TM format of the SDL alignment tool",
        "tmx": "TMX", "tbx": "Term Base eXchange", "xces": "XCES", "xhtml": "XHTML", "xmi": "XMI", "xml": "XML"
    },
    "multilinguality": {
        "prl": "Parallel", "comp": "Comparable", "mst": "Multilingual Single Text"
    },
    "resourceType": {
        "crp": "corpus", "lcr": "lexicalConceptualResource", "ld": "languageDescription"
    },
    "textType": {
        "aca": "academicTexts", "admin": "administrativeTexts", "blog": "blogTexts", "chat": "chatTexts",
        "encycl": "encyclopaedicTexts", "ffcd": "faceToFaceConversationsDiscussions", "journal": "journalisticTexts",
        "literar": "literaryTexts", "meeting": "meetingProceedings", "tech": "technicalTexts",
        "telephone": "telephoneConversations"
    }
}


def get_language_name(lang_code):
    return get_language_by_subtag(lang_code)


def get_domain_description(domain):
    return get_domain_by_id(domain)


def encode_filter(key, value):
    try:
        in_filter = haystack_filters['filters'][key]
    except KeyError:
        in_filter = key

    if key == 'lang' or key == 'language':
        value = get_language_by_subtag(value) or value
    elif key == 'domain':
        value = get_domain_by_id(value) or value
    else:
        try:
            value = haystack_filters[key][value]
        except KeyError:
            # return the value as is
            pass
    return {
        'filter': in_filter,
        'value': value
    }
