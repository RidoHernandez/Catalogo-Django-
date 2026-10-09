from django import template
from inventario.permissions import has_role

register = template.Library()

@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr, '')

@register.filter
def has_role_filter(user, role):
    return has_role(user, role)
