print("Loading custom_tags.py")

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, *args):
    request = context['request']
    for path in args:
        if request.path.startswith(path):
            return 'active'
    return ''
