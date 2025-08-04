from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('register/', views.register_organization, name='register'),
    path('register/success/', views.registration_success, name='registration_success'),
]