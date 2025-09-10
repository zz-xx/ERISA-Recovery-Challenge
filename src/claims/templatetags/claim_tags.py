from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_url(context, field_name: str) -> str:
    """
    Generates a URL for a table header to handle sorting.

    It preserves all existing filter/search query parameters and toggles
    the sort direction for the given field.

    Args:
        context: The template context, which must contain the `request` object.
        field_name: The name of the model field to sort by.

    Returns:
        A URL-encoded string for the href attribute of a link.
        e.g., "?search=acme&status=PAID&sort=-billed_amount"
    """
    request = context["request"]
    query_params = request.GET.copy()

    current_sort = query_params.get("sort", "")

    if current_sort.lstrip("-") == field_name:
        # The current field is being sorted, so reverse the direction.
        if current_sort.startswith("-"):
            query_params["sort"] = field_name  # From descending to ascending.
        else:
            query_params["sort"] = f"-{field_name}"  # From ascending to descending.
    else:
        # It's a new field, so default to ascending.
        query_params["sort"] = field_name

    return f"?{query_params.urlencode()}"


@register.simple_tag(takes_context=True)
def sort_indicator(context, field_name: str) -> str:
    """
    Returns an HTML SVG arrow to indicate the current sort field and direction.

    Args:
        context: The template context, which must contain the `request` object.
        field_name: The name of the model field for the indicator.

    Returns:
        An HTML string for an SVG arrow if the field is being sorted,
        otherwise an empty string.
    """
    request = context["request"]
    current_sort = request.GET.get("sort", "")

    if current_sort.lstrip("-") == field_name:
        if current_sort.startswith("-"):
            # Descending Arrow
            svg = '<svg width="10" height="10" viewBox="0 0 24 24" style="vertical-align: middle;"><path d="M12 21l12-18h-24z"/></svg>'
            return mark_safe(svg)
        else:
            # Ascending Arrow
            svg = '<svg width="10" height="10" viewBox="0 0 24 24" style="vertical-align: middle;"><path d="M12 3l-12 18h24z"/></svg>'
            return mark_safe(svg)
    return ""


@register.filter(name="split")
def split(value: str, key: str = " ") -> list[str]:
    """
    A simple template filter that splits a string into a list of strings.

    Usage: {{ some_string|split:"," }}
    """
    return value.split(key)
