from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def admin_urlname(value, arg):
    """Return admin URL name for given model and action"""
    app_label = value.app_label
    model_name = value.model_name
    return f"admin:{app_label}_{model_name}_{arg}"