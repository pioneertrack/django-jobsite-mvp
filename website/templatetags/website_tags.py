from django import template

register = template.Library()

@register.assignment_tag
def to_list(*args):
    return list(args)
