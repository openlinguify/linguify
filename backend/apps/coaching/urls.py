from django.urls import path
from django.http import HttpResponse

# Placeholder view for coaching app
def coaching_placeholder(request):
    return HttpResponse("""
    <h1>Coaching App</h1>
    <p>Cette application coaching est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = 'coaching'

urlpatterns = [
    path('', coaching_placeholder, name='coaching_home'),
]