import logging

from django.contrib.auth import views as auth_views
from django.shortcuts import render_to_response
from django.template import RequestContext
from metashare.repository.models import resourceInfoType_model
from metashare.settings import LOG_HANDLER, COUNTRY, LANGUAGE_CODE
from metashare.storage.models import PUBLISHED


# Setup logging support.
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOG_HANDLER)


def frontpage(request):
    """Renders the front page view."""
    LOGGER.info(LANGUAGE_CODE)
    request.session['django_language'] = LANGUAGE_CODE
    LOGGER.info(u'Rendering frontpage view for user "{0}".'
                .format(request.user.username or "Anonymous"))
    lr_count = resourceInfoType_model.objects.filter(
        storage_object__publication_status=PUBLISHED,
        storage_object__deleted=False).count()
    dictionary = {'country': COUNTRY}
    return render_to_response('frontpage.html', dictionary,
      context_instance=RequestContext(request))


def login(request, template_name):
    """Renders login view by connecting to django.contrib.auth.views."""
    LOGGER.info(u'Rendering login view for user "{0}".'.format(
      request.user.username or "Anonymous"))

    return auth_views.login(request, template_name)


def logout(request):
    """Renders logout view by connecting to django.contrib.auth.views."""
    LOGGER.info(u'Logging out user "{0}", redirecting to /.'.format(
      request.user.username or "Anonymous"))

    return auth_views.logout(request, 'frontpage')
