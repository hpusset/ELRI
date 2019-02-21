from os import walk
from os import environ
from os.path import abspath, dirname, join
import tempfile

from django.utils.translation import ugettext_lazy as _

from metashare.bcp47 import iana

ROOT_PATH = abspath(dirname(__file__))

# The URL for this META-SHARE node django application.  Do not use trailing /.
# This URL has to include DJANGO_BASE (without its trailing /)!
DJANGO_URL = environ['ELRI_PROTOCOL'] + '://' + environ['ELRI_HOSTNAME'] + '.' + environ['ELRI_DOMAINNAME']

# The base path under which django is deployed at DJANGO_URL.  Use trailing /.
# Do not use leading / though.  Leave empty if META-SHARE is deployed directly
# under the given DJANGO_URL.
DJANGO_BASE = ''

# Required if deployed with lighttpd.
# FORCE_SCRIPT_NAME = ""

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
USE_L10N = True

# one of the supported countries
# one wants to make sure the country is among the EU countries
COUNTRY = filter(lambda country: country == environ['ELRI_COUNTRY'], iana.get_eu_regions())[0]

USE_I18N = True

LANGUAGE_CODE = environ['ELRI_LANGUAGE'] # one of the LANGUAGES language codes

# Supported localisation languages
LANGUAGES = (
    ('es-es', _('Spanish')),
    ('en-ie', _('English')),
    ('fr-fr', _('French')),
    ('ga-ie', _('Gaelic')),
    ('pt-pt', _("Portuguese")),
)

# Supported processing languages
lang_list = environ['ELRI_SUP_LANGUAGES']
import ast
SUPPORTED_LANGUAGES = ast.literal_eval(lang_list)


# Directories containing the translations
LOCALE_PATHS = tuple([
    join(directory, dn)
    for directory, dns, _ in walk(abspath(dirname(__file__)))
    for dn in dns
    if dn == "locale"
])

# Path to the local storage layer path used for persistent object storage.
STORAGE_PATH = '/elri/elri_resources/language_resources'

# Path to the local directory where all the static files (images, js, css) will 
# be collected and served by the web server in STATIC_URL
STATIC_ROOT = '/elri/static'

# Directory in which lock files will temporarily be created.
LOCK_DIR = join(tempfile.gettempdir(), 'metashare-locks')

# Debug settings, setting DEBUG=True will give exception stacktraces.
DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_JS = DEBUG
SECRET_KEY = environ['ELRI_SALT']
LOG_FILENAME = join(tempfile.gettempdir(), "metashare.log")

# Configure administrators for this django project.  If DEBUG=False, errors
# will be reported as emails to these persons...
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# configure the database to use (see
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases for details)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql',
                                         # 'sqlite3', 'oracle'.
        'NAME': environ['DBELRI_NAME'],                      # database name -- or path to file if
                                         # using sqlite3, e.g.
                                         # '{0}/testing.db'.format(ROOT_PATH)
#        'TEST_NAME': 'elri_test',                 # test database name -- or path to file
                                         # if using sqlite3, e.g.
                                         # '{0}/testing2.db'.format(ROOT_PATH)
                                         # mandatory when using Selenium tests
        'USER': environ['DBELRI_USER'],                      # Not used with sqlite3.
        'PASSWORD': environ['DBELRI_PASS'],                  # Not used with sqlite3.
        'HOST': 'postgres-server',                      # Set to 'localhost' for localhost.
                                         # Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default.
                                         # Not used with sqlite3.
    }
}

# the URL of the Solr server (or server core) which is used as a search backend
SOLR_URL = 'http://solr:8983/solr/main'
# the URL of the Solr server (or server core) which is used as a search backend
# when running tests
TESTING_SOLR_URL = 'http://solr:8983/solr/testing'

# Instead of using an email server, print emails to server console:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For testing, use a builtin email server (not for production use):
# EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# For production use, you have to configure a proper mail server:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#
# See the Django documentation for more details:
# - https://docs.djangoproject.com/en/1.3/topics/email/#smtp-backend

EMAIL_USE_TLS = environ['ELRI_EMAIL_TLS'].lower() == 'true'
EMAIL_HOST = environ['ELRI_EMAIL_HOST']
EMAIL_PORT = environ['ELRI_EMAIL_PORT']
EMAIL_HOST_USER = environ['ELRI_EMAIL_USER']
EMAIL_HOST_PASSWORD = environ['ELRI_EMAIL_PASS']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = environ['ELRI_TIMEZONE']

# The location of the xdiff tool to compare XML files.
XDIFF_LOCATION = "{0}/../misc/tools/xdiff-src/xdiff".format(ROOT_PATH)

# The web browser to use for the Selenium tests; possible values are:
# Firefox, Ie, Opera, Chrome
SELENIUM_DRIVER = 'Firefox'

# The port of the Selenium test server;
# this must be the same port as used in DJANGO_URL
SELENIUM_TESTSERVER_PORT = 8000

# Settings for synchronization:
# Time interval settings. It sets the intervals when the synchronization 
# task will be triggered. Uses "crontab" conventions. 
# Defaults will run the synchronization task once an hour.
SYNC_INTERVALS = {
    'MINUTE' : '25',      # 0-59 - Default is 25
    'HOUR' : '*',         # 0-23 - Default is *
    'DAY_OF_MONTH' : '*', # 1-31 - Default is *
    'MONTH' : '*',        # 1-12 - Default is *
    'DAY_OF_WEEK' : '*',  # 0-6 (0 is Sunday) - Default is *
}

# Settings for digest updating:
# Time interval settings. It sets the intervals when the digest updating  
# task will be triggered. Uses "crontab" conventions. 
# Defaults will run the updating task twice a day.
# The update intervals should roughly be half of the MAX_DIGEST_AGE as
# defined below
UPDATE_INTERVALS = {
    'MINUTE' : '59',      # 0-59 - Default is 59
    'HOUR' : '*/12',      # 0-23 - Default is */12
    'DAY_OF_MONTH' : '*', # 1-31 - Default is *
    'MONTH' : '*',        # 1-12 - Default is *
    'DAY_OF_WEEK' : '*',  # 0-6 (0 is Sunday) - Default is *
}

# Maximum age of digests in storage folder in seconds
MAX_DIGEST_AGE = 60 * 60 * 24

# List of other META-SHARE Managing Nodes from which the local node imports
# resource descriptions. Any remote changes will later be updated
# ("synchronized"). Use this if you are a META-SHARE Managing Node!
# Important: make sure to use node IDs which are unique across both CORE_NODES
#            and PROXIED_NODES!
CORE_NODES = {
#    'node_id_1': {
#        'NAME': 'AUNI',                       # The short name of the node.
#        'DESCRIPTION': 'xxx',                 # A short descpription of the node.
#        'URL': 'http://metashare.example.com:8000', # The URL of the other
#                                              # META-SHARE Managing Node (also
#                                              # include the port if needed).
#        'USERNAME': 'sync-user-1',            # The name of a sync user on 
#                                              # the META-SHARE Managing Nodes.
#        'PASSWORD': 'sync-user-pass',         # Sync user's password.
#    },
#    'node_id_2': {
#        'NAME': 'BUNI',                     
#        'DESCRIPTION': 'xxx',               
#        'URL': 'http://example.com/pub/metashare',
#        'USERNAME': 'sync-user-2',
#        'PASSWORD': 'sync-user-pass-2',
#    },
}

# User accounts with the permission to access synchronization information on
# this node; whenever you change this setting, make sure to run
# "manage.py syncdb" for the changes to take effect!
SYNC_USERS = {
    #'syncuser1': 'secret',
    #'syncuser2': 'alsosecret',
}

# List of other META-SHARE Nodes from which the local node imports resource
# descriptions. Any remote changes will later be updated ("synchronized"). Any
# imported resource descriptions will also be shared with other nodes that
# synchronize with this local node, i.e., this node acts as a proxy for the
# listed nodes. This setting is meant to be used by META-SHARE Managing Nodes
# which make normal META-SHARE Node resource descriptions available on the
# META-SHARE Managing Nodes.
# Important: make sure to use node IDs which are unique across both CORE_NODES
#            and PROXIED_NODES!
PROXIED_NODES = {
#    'proxied_node_id_1': {
#        'NAME': 'Proxied Node 1',
#        'DESCRIPTION': 'xxx',
#        'URL': 'http://metashare.example.org',
#        'USERNAME': 'sync-user-3',
#        'PASSWORD': 'sync-user-pass-3',
#    },
}

# You cann add custom web analytics application settings here through the Django
# Analytical framework which is integrated in META-SHARE. By default, all
# META-SHARE services are monitored with a common Google Analytics tracking
# code; see the Installation Manual for more information on this.
# For the integration of other web analytics services' options, see
# <http://packages.python.org/django-analytical/>.
#
CONTRIBUTIONS_ALERT_EMAILS = [environ['ELRI_ALERT_MAILS']]

TMP = "/tmp"

CONTRIBUTION_FORM_DATA = "/elri/metashare"
DOCUMENTATION_ROOT="/elri"

# Immaterial for launching the application
AP_CERTS_DIR = "/certificates"

PARTNERS = ["partner_1", "partner_2"]

# Immaterial for launching the application
ELRC_CERT = AP_CERTS_DIR + "cert_file.txt"

# Just for honoring the code needs. To remove or update if needed
# To get a working instance of the basic app, they can be left as such.
ADD_COMMAND = "{0}{1}{2}{3}"
REMOVE_COMMAND = "{0}{1}{2}"

TRUSTORE_FILE = ""
TRUSTSTORE_PASSWORD = ""

AP_URL = ""
REST_PASSWORD = ""
REST_USERNAME = ""
REST_LOGIN_URL = ""
REST_AUTH_URL = ""
PMODE_POST_URL = ""
TRUSTSTORE_POST_URL = ""
PMODE_FILE = ""

LEGAL_REVIEWERS = ("1",)

REST_API_KEY = ""

ALLOWED_HOSTS = ['elri-node1', 'localhost']

DOC2TMX_URL = "http://toolchain:8080/ELRI_WebService/tc_doc2tmx/process"
TM2TMX_URL = "http://toolchain:8080/ELRI_WebService/tc_tm2tmx/process"
