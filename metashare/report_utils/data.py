# coding=utf-8
from collections import OrderedDict

types = OrderedDict({"Corpus Monolingual": 0, "Corpus Bilingual": 0, "Corpus Multilingual": 0, "Lexical Monolingual": 0,
                     "Lexical Bilingual": 0, "Lexical Multilingual": 0, "Language Description Monolingual": 0})

all_domains = {"BUSINESS & COMPETITION": 0, "INTERNATIONAL RELATIONS": 0, "EDUCATION & COMMUNICATIONS": 0,
               "PRODUCTION, TECHNOLOGY & RESEARCH": 0, "LAW": 0, "POLITICS": 0, "EMPLOYMENT & WORKING CONDITIONS": 0,
               "EUROPEAN UNION": 0, "SOCIAL QUESTIONS": 0, "FINANCE": 0, "TRANSPORT": 0, "ECONOMICS": 0, "INDUSTRY": 0,
               "AGRICULTURE, FORESTRY & FISHERIES": 0, "GEOGRAPHY": 0, "SCIENCE": 0, "TRADE": 0,
               "ENVIRONMENT": 0, "AGRI-FOODSTUFFS": 0, "INTERNATIONAL ORGANISATIONS": 0, "ENERGY": 0}

all_countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                 "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia",
                 "Lithuania", "Luxembourg", "Malta", "Netherlands", "Norway", "Poland", "Portugal", "Romania",
                 "Slovakia", "Slovenia", "Spain", "Sweden", "United Kingdom"]
all_languages = {
    u"Bulgarian": {}, u"Czech": {}, u"Croatian": {}, u"Danish": {}, u"Dutch; Flemish": {}, u"English": {},
    u"Estonian": {}, u"Finnish": {}, u"French": {}, u"German": {}, u"Hungarian": {}, u"Icelandic": {}, u"Irish": {},
    u"Italian": {}, u"Latvian": {},
    u"Lithuanian": {}, u"Maltese": {}, u"Modern Greek (1453-)": {}, u"Norwegian": {}, u"Norwegian Bokmål": {},
    u"Norwegian Nynorsk": {},
    u"Polish": {}, u"Portuguese": {},
    u"Romanian; Moldavian; Moldovan": {}, u"Slovak": {}, u"Slovenian": {}, u"Spanish; Castilian": {}, u"Swedish": {}
}

lang_dict = {
    l: OrderedDict(types.copy()) for l in all_languages
    }

excel_matrix = {
    "country_row": OrderedDict({
        "Austria": 2, "Belgium": 3, "Bulgaria": 4, "Croatia": 5, "Cyprus": 6, "Czech Republic": 7,
        "Denmark": 8, "Estonia": 9, "Finland": 10, "France": 11, "Germany": 12,
        "Greece": 13, "Hungary": 14, "Iceland": 15, "Ireland": 16, "Italy": 17,
        "Latvia": 18, "Lithuania": 19, "Luxembourg": 20, "Malta": 21, "Netherlands": 22,
        "Norway": 23, "Poland": 24, "Portugal": 25, "Romania": 26, "Slovakia": 27,
        "Slovenia": 28, "Spain": 29, "Sweden": 30, "United Kingdom": 31
    }),
    "type_col": OrderedDict({
        "Language Description Monolingual": 1, "Corpus Bilingual": 2,
        "Lexical Monolingual": 3, "Lexical Multilingual": 4,
        "Corpus Multilingual": 5, "Lexical Bilingual": 6,
        "Corpus Monolingual": 7
    }),
    "domain_col": OrderedDict({
        "PRODUCTION, TECHNOLOGY & RESEARCH": 1, "SOCIAL QUESTIONS": 2, "ECONOMICS": 3,
        "INTERNATIONAL RELATIONS": 4, "FINANCE": 5, "EMPLOYMENT & WORKING CONDITIONS": 6,
        "INTERNATIONAL ORGANISATIONS": 7, "SCIENCE": 8, "INDUSTRY": 9,
        "BUSINESS & COMPETITION": 10, "TRADE": 11, "ENVIRONMENT": 12,
        "EDUCATION & COMMUNICATIONS": 13, "AGRI-FOODSTUFFS": 14, "AGRICULTURE, FORESTRY & FISHERIES": 15,
        "POLITICS": 16, "LAW": 17, "EUROPEAN UNION": 18, "ENERGY": 19,
        "TRANSPORT": 20, "GEOGRAPHY": 21,
    }),
    "dsi_col": {
        "ElectronicExchangeOfSocialSecurityInformation": 1, "saferInternet": 2,
        "BusinessRegistersInterconnectionSystem": 3, "eJustice": 4,
        "OnlineDisputeResolution": 5, "eProcurement": 6,
        "Cybersecurity": 7, "eHealth": 8,
        "OpenDataPortal": 9, "Europeana": 10
    }
}
