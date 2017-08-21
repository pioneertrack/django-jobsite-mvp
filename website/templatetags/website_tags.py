from django import template

register = template.Library()

@register.assignment_tag
def to_list(*args):
    return list(args)

@register.assignment_tag
def in_list(*args):
    val = args[0].get(args[1])
    return val