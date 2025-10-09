from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'monetization'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='monetization:dashboard', permanent=False), name='index'),
    path('dashboard/', views.EarningsDashboardView.as_view(), name='dashboard'),
    path('sales/', views.SalesListView.as_view(), name='sales'),
    path('payouts/', views.PayoutListView.as_view(), name='payouts'),
]