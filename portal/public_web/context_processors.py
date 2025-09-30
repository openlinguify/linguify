"""
Context processors for public_web app
"""
import os


def app_urls(request):
    """
    Add app URLs to template context based on environment
    Uses existing *_API_URL variables from .env
    """
    backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8081')
    lms_url = os.getenv('LMS_API_URL', 'http://localhost:8001')

    # Build feedback URL from backend URL
    feedback_url = f'{backend_url}/auth/feedback/'

    return {
        'FEEDBACK_URL': feedback_url,
        'BACKEND_URL': backend_url,
        'LMS_URL': lms_url,
    }