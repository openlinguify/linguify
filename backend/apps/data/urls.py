from django.urls import path
from django.http import HttpResponse

# Placeholder view for data app
def data_placeholder(request):
    return HttpResponse("""
    <h1>Data</h1>
    <p>Cette application Data est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = 'data'

urlpatterns = [
    path('', data_placeholder, name='data_home'),
]