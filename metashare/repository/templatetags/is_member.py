from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='is_member')
def is_member(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return True if group in user.groups.all() else False
    except Group.DoesNotExist:
        # If no group named group_name exists, then it cannot have user as
        # a member
        return False
