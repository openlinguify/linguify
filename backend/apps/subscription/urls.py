from django.urls import path
from django.http import HttpResponse

# Placeholder view for subscription app
def subscription_placeholder(request):
    return HttpResponse("""
    <h1>Subscription</h1>
    <p>Cette application Subscription est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = 'subscription'

urlpatterns = [
    path('', subscription_placeholder, name='subscription_home'),
]