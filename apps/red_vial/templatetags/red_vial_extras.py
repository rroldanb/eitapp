from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter to access dict items by key: {{ dict|get_item:key }}"""
    try:
        return dictionary.get(str(key), 0)
    except (AttributeError, TypeError):
        try:
            return dictionary[key]
        except (KeyError, TypeError, IndexError):
            return 0
