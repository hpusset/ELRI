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


# def validate_cer_file(value):
#     if not value.lower().endswith(".cer"):
#         raise ValueError(u'The file you are trying to upload does not'
#                          u'appear to be a ".cer" file.')
