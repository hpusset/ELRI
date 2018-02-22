import re

from django.core.exceptions import ValidationError
from urllib2 import urlopen
from django.http import Http404


def validate_wsdl_url(value):
    if value.lower().endswith("/msh"):
        try:
            urlopen(value)
        except Http404:
            raise ValidationError(u'%s does not exist' % value)
        except:
            raise ValidationError(u'%s does not exist' % value)
    else:
        raise ValidationError(u'%s is not a valid WSDL endpoint. '
                              u'Please make sure that you have added \"/msh\" '
                              u'at the end of the URL.' % value)



