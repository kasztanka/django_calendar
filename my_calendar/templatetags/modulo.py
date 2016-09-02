from django import template
register = template.Library()

@register.filter
def modulo(number, value):
    return number % value