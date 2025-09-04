from django.urls import path
from django.http import HttpResponse

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
]