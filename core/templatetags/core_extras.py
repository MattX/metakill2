from django import template

register = template.Library()


@register.filter
def user(u):
    if u.first_name:
        return u.first_name
    else:
        return u.username
