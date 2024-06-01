# custom_tags.py
from django import template

register = template.Library()

@register.filter
def to_range(value, max_value):
    return range(value, max_value)
