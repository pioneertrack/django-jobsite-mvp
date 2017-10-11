from django import template

register = template.Library()


@register.assignment_tag
def get(*args):
    return args[0].get(args[1], None)