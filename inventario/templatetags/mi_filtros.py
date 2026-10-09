from django import template

register = template.Library()

@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr, '')

@register.filter
def has_group(user, group_name):
    return (
        getattr(user, "is_authenticated", False)
        and user.groups.filter(name=group_name).exists()
    )
