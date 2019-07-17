from os.path import abspath, dirname
ROOT_PATH = abspath(dirname(__file__))

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from django.core.urlresolvers import reverse_lazy


# Import local settings, i.e., DEBUG, TEMPLATE_DEBUG, TIME_ZONE,
# DATABASE_* settings, ADMINS, etc.
from local_settings import *

# Allows to disable check for duplicate instances.
CHECK_FOR_DUPLICATE_INSTANCES = True

# Logging settings for this Django project.
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s] %(name)s::%(levelname)s %(message)s"
LOG_DATE = "%m/%d/%Y @ %H:%M:%S"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT, LOG_DATE)

# Allows to disable check for duplicate instances.
CHECK_FOR_DUPLICATE_INSTANCES = True

# work around a problem on non-posix-compliant platforms by not using any
# RotatingFileHandler there
if os.name == "posix":
    LOG_HANDLER = RotatingFileHandler(filename=LOG_FILENAME, mode="a",
        maxBytes=1024*1024, backupCount=5, encoding="utf-8")
else:
    LOG_HANDLER = logging.FileHandler(filename=LOG_FILENAME, mode="a",
        encoding="utf-8")
LOG_HANDLER.setLevel(level=LOG_LEVEL)
LOG_HANDLER.setFormatter(LOG_FORMATTER)

# init root logger
logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_DATE, level=LOG_LEVEL)

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Maximum size of files uploaded as resrouce data.
# The default is a cautious value in order to protect the server
# against resource starvation; if you think your server can handle
# bigger files, feel free to try and increase this value.
MAXIMUM_UPLOAD_SIZE = 400 * 1024 * 1024

# Synchronization info:
SYNC_NEEDS_AUTHENTICATION = True

# URL for the Metashare Knowledge Base
KNOWLEDGE_BASE_URL = 'http://www.meta-share.org/knowledgebase/'

# The URL for META-SHARE statistics server.
STATS_SERVER_URL = "http://metastats.fbk.eu/"

# The URL for GeoIP database.
GEOIP_DATA_URL = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz"


# If STORAGE_PATH does not exist, try to create it and halt if not
# possible.
try:
    if not os.path.isdir(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)
    if not os.path.isdir(LOCK_DIR):
        os.makedirs(LOCK_DIR)
except:
    raise OSError, "STORAGE_PATH must exist and be writable!"

# If XDIFF_LOCATION was not set in local_settings, set a default here:
try:
    _ = XDIFF_LOCATION
except:
    XDIFF_LOCATION = None

# Perform some cleanup operations on the imported local settings.
if DJANGO_URL.strip().endswith('/'):
    DJANGO_URL = DJANGO_URL.strip()[:-1]

if not DJANGO_BASE.strip().endswith('/'):
    DJANGO_BASE = '{0}/'.format(DJANGO_BASE.strip())

if DJANGO_BASE.strip().startswith('/'):
    DJANGO_BASE = DJANGO_BASE.strip()[1:]

# Pagination settings for this django project.
PAGINATION_ITEMS_PER_PAGE = 50

LOGIN_URL = '/{0}login/'.format(DJANGO_BASE)
LOGIN_REDIRECT_URL = reverse_lazy('frontpage') # reverse it to grab the i18n prefix
LOGOUT_URL = '/{0}logout/'.format(DJANGO_BASE)

MANAGERS = ADMINS

SITE_ID = 1

METASHARE_VERSION = '3.1.1'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.

STATIC_URL = '/static/'

STATICFILES_DIRS = ( '{0}/static/'.format(ROOT_PATH),)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'django_password_validation.DjangoPasswordValidationMiddleware', # must come before AuthenticationMiddleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'metashare.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '{0}/templates'.format(ROOT_PATH),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "metashare.context_processors.global_settings",
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',

    'selectable',
    'haystack',
    'analytical',
    'tastypie',

    'metashare.accounts',
    'metashare.storage',
    # 'metashare.sync',
    'metashare.stats',
    'metashare.recommendations',
    'metashare.repository',
    'metashare.bcp47',
    # 'metashare.processing',
    'progressbarupload',
    'metashare.edelivery',
    # PROJECT MANAGEMENT
    'project_management',
)

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
    "progressbarupload.uploadhandler.ProgressBarUploadHandler",
)

# add Kronos to installed apps if not running on Windows
if os.name != 'nt':
    INSTALLED_APPS += ('kronos',)

# basic Haystack search backend configuration
TEST_MODE_NAME = 'testing'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': SOLR_URL,
        'SILENTLY_FAIL': False
    },
    TEST_MODE_NAME: {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': TESTING_SOLR_URL,
        'SILENTLY_FAIL': False
    },
}

# This setting controls what haystack SignalProcessor class is used to handle
# Django's signals and keep the search index up-to-date.
HAYSTACK_SIGNAL_PROCESSOR = 'metashare.repository.signals.PatchedSignalProcessor'

# we use a custom Haystack search backend router so that we can dynamically
# switch between the main/default search backend and the one for testing
HAYSTACK_ROUTERS = [ 'metashare.haystack_routers.MetashareRouter' ]

# a custom test runner with the added value on top of the default Django test
# runner to automatically set up Haystack so that it uses a dedicated search
# backend for testing
TEST_RUNNER = 'metashare.test_runner.MetashareTestRunner'

PYLINT_RCFILE = '{0}/test-config/pylint.rc'.format(ROOT_PATH)

# set display for Selenium tests
if 'DISPLAY' in os.environ:
    import re
    SELENIUM_DISPLAY = re.sub(r'[^\:]*(\:\d{1,2})(?:\.\d+)?', r'\1',
      os.environ['DISPLAY'])

# sitemap url to be used in "robots.txt"
SITEMAP_URL = '{}/sitemap.xml'.format(DJANGO_URL)

# maximum time interval in seconds allowed between two resource views so that
# the resources are still considered as 'viewed together';
# used in recommendations
MAX_VIEW_INTERVAL = 60 * 5

# maximum time interval in seconds allowed between two resource downloads so
# that the resources are still considered as 'downloaded together';
# used in recommendations
MAX_DOWNLOAD_INTERVAL = 60 * 10

# list of synchronization protocols supported by this node
SYNC_PROTOCOLS = (
    '1.0',
)

# Full import path of a serializer class to use for serializing session data
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# The Python path syntax of the setting we are using in META-SHARE
DJANGO_SETTINGS_MODULE = 'metashare.settings'

# A dictionary specifying the package where migration modules can be found
# on a per-app basis.
MIGRATION_MODULES = {
    'accounts': 'metashare.accounts.django_migrations',
    'repository': 'metashare.repository.django_migrations',
    'stats': 'metashare.stats.django_migrations',
    'recommendations': 'metashare.recommendations.django_migrations',
    'storage': 'metashare.storage.django_migrations',
}

class DisableMigrations(object):

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"

TESTS_IN_PROGRESS = False
if 'test' in sys.argv[1:]:
    logging.disable(logging.CRITICAL)
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG
    TESTS_IN_PROGRESS = True
    MIGRATION_MODULES = DisableMigrations()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

TASTYPIE_ALLOW_MISSING_SLASH = True
TASTYPIE_DEFAULT_FORMATS = ['json']



ELRC_API_USERNAME = os.environ.get('ELRC_API_USERNAME', None)
ELRC_API_PASSWORD = os.environ.get('ELRC_API_PASSWORD', None)
