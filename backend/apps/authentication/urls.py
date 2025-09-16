from django.urls import path
from django.http import HttpResponse
from .views.terms_views import terms_acceptance_view, accept_terms_ajax, terms_status_web, accept_terms_web

# Placeholder view for authentication app
def authentication_placeholder(request):
    return HttpResponse("""
    <h1>Authentication</h1>
    <p>Cette application Authentication est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = 'authentication'

urlpatterns = [
    path('', authentication_placeholder, name='authentication_home'),

    # Terms of Use URLs
    path('terms/accept/', terms_acceptance_view, name='terms_acceptance'),
    path('terms/accept/ajax/', accept_terms_ajax, name='accept_terms_ajax'),
    path('terms/status/', terms_status_web, name='terms_status'),
    path('terms/accept/web/', accept_terms_web, name='accept_terms_web'),
]