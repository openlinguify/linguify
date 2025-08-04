from django.urls import path
from . import views

app_name = 'monetization'

urlpatterns = [
    path('dashboard/', views.EarningsDashboardView.as_view(), name='dashboard'),
    path('sales/', views.SalesListView.as_view(), name='sales'),
    path('payouts/', views.PayoutListView.as_view(), name='payouts'),
]