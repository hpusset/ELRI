from django import template
from django.conf import settings
import logging


LOG = logging.getLogger(__name__)


register = template.Library()


@register.assignment_tag
def get_email(name):
    """Returns a configured email address.

    Remarks from author: assignment_tag has been
    deprecated in Django==1.9 and removed from
    Django>=2.0 but is the correct way to implement
    this functionality in Django<1.9.
    when using Django>= 1.9, replace with simple_tag.
    """
    if name not in settings.EMAIL_ADDRESSES:
        LOG.warn(
            "email address '%s' not configured in settings.EMAIL_ADDRESSES",
            name,
        )
        return ""
    return settings.EMAIL_ADDRESSES[name]
