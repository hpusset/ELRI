from os.path import dirname
from lxml import etree
from metashare.settings import ROOT_PATH

path = '{0}/'.format((dirname(ROOT_PATH)))

domains = etree.parse('{}metashare/eurovoc/domains.xml'.format(path))

# DOMAINS and respective subdomains

def get_all_domains():
    xpath = u"//domains/domain/description/text()"
    return domains.xpath(xpath)

def get_all_subdomains():
    xpath = u"//subdomain/description/text()"
    return domains.xpath(xpath)


def get_subdomains_by_domain(dom):
    xpath = u"//domains/domain[description='{}']/subdomains//subdomain/description/text()".format(dom)
    return domains.xpath(xpath)

def get_domain_by_subdomain(subd):
    xpath = u"//domains/domain[subdomains//subdomain/description='{}']/description/text()".format(subd)
    return ''.join(domains.xpath(xpath))


def get_subdomain_by_subsubdomain(subsub):
    xpath = u"//domains/domain/subdomains/subdomain[subsub='{}']/description/text()".format(subsub)
    return ''.join(domains.xpath(xpath))

def get_domain_id(domain):
    xpath = u"//domain[description='{}']/@id".format(domain)
    return ''.join(domains.xpath(xpath))

def get_subdomain_id(subdomain):
    xpath = u"//subdomain[description='{}']/@id".format(subdomain)
    return ''.join(domains.xpath(xpath))