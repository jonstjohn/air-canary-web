from django import template

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
@stringfilter
def space2br(value):
    """Convert spaces into html <br/>
    """
    return mark_safe(value.replace(' ', '<br/>'))
