import locale
from django import template
register = template.Library()
locale.setlocale(locale.LC_ALL, '')


@register.filter
def to_currency(value):
    return locale.currency(value, grouping=True)
