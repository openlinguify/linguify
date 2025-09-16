# backend/core/subscription/urls.py
from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    # Pages d'abonnement
    path('plans/', views.subscription_plans, name='plans'),
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='checkout'),
    path('success/', views.subscription_success, name='success'),
    path('manage/', views.manage_subscription, name='manage'),

    # Webhook Stripe
    path('webhook/', views.stripe_webhook, name='webhook'),

    # API
    path('api/status/', views.SubscriptionAPI.as_view(), name='api_status'),
]