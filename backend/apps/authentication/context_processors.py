"""
Context processors for authentication templates
"""
from django.conf import settings
from django.utils import translation


def auth_context(request):
    """
    Add authentication-related context variables to templates
    """
    return {
        'PORTAL_URL': settings.PORTAL_URL,
        'CONTACT_URL': f"{settings.PORTAL_URL}/{translation.get_language()}/contact/",
    }