from django import template

register = template.Library()

def dq_to_sq(value):
    rendered = str(value.replace("\"","'"))
    return rendered

register.filter('dq_to_sq', dq_to_sq)

def set_attribute(value, arg):
    attrs = value.field.widget.attrs
    attrs['title'] = arg
    rendered = str(value)
    return rendered

register.filter('set_attribute', set_attribute)
