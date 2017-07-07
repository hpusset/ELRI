from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='url_target')
def url_target(text, target, autoescape=True):
    return  mark_safe(text.replace('<a ', '<a target="{}" '.format(target)))