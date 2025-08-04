from django import template

register = template.Library()

@register.filter
def intdot(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", ".")
    except:
        return value

@register.filter 
def to(start, end):
    return range(start, end + 1)