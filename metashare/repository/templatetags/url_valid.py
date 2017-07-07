from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='url_valid')
def url_valid(text):
    text_stripped = text.strip()
    if not str(text_stripped).startswith("http://") and \
            not str(text_stripped).startswith("https://") and \
            not str(text_stripped).startswith("ftp://") and \
            not str(text_stripped).startswith("sftp://"):

            return "http://{}".format(text_stripped)
    else:
        return text_stripped