from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dict by key in template."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, set())
    return set()


@register.filter
def in_set(value, the_set):
    """Check if value is in set."""
    if isinstance(the_set, (set, list)):
        return value in the_set
    return False