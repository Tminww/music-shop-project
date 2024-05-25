from django import template

register = template.Library()


@register.filter
def create_range(value, start_index=0):
    return range(start_index, int(value) + start_index)
