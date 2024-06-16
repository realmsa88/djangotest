# In your custom_filters.py file
from django import template

register = template.Library()

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def number_range(start, end):
    return range(start, end + 1)