from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def sort_url(context, field_name):
    """
    Generates a URL for sorting, preserving all other filters.
    Toggles the sort direction for the given field.
    """
    request = context['request']
    query_params = request.GET.copy()

    # Robustly get the sort parameter, defaulting to 'id' if it's missing or empty
    current_sort = request.GET.get('sort')
    if not current_sort:
        current_sort = 'id'
    
    if current_sort.lstrip('-') == field_name:
        # It's the current sort field, so toggle direction
        if current_sort.startswith('-'):
            query_params['sort'] = field_name  # From desc to asc
        else:
            query_params['sort'] = f"-{field_name}"  # From asc to desc
    else:
        # It's a new field, so default to ascending
        query_params['sort'] = field_name

    return f"?{query_params.urlencode()}"


@register.simple_tag(takes_context=True)
def sort_indicator(context, field_name):
    """
    Returns an HTML SVG arrow indicating the current sort direction.
    """
    request = context['request']
    
    # Robustly get the sort parameter, defaulting to 'id' if it's missing or empty
    current_sort = request.GET.get('sort')
    if not current_sort:
        current_sort = 'id'
    
    if current_sort.lstrip('-') == field_name:
        if current_sort.startswith('-'):
            # Descending Arrow
            svg = '<svg width="10" height="10" viewBox="0 0 24 24" style="vertical-align: middle;"><path d="M12 21l12-18h-24z"/></svg>'
            return mark_safe(svg)
        else:
            # Ascending Arrow
            svg = '<svg width="10" height="10" viewBox="0 0 24 24" style="vertical-align: middle;"><path d="M12 3l-12 18h24z"/></svg>'
            return mark_safe(svg)
    return ""


@register.filter(name='split')
def split(value, key=' '):
    """
    Returns the value turned into a list.
    """
    return value.split(key)