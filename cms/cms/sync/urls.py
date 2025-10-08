from django.urls import path
from . import views

app_name = 'sync'

urlpatterns = [
    path('status/', views.SyncStatusView.as_view(), name='status'),
    path('sync-all/', views.SyncAllView.as_view(), name='sync_all'),
    path('sync-unit/<int:unit_id>/', views.SyncUnitView.as_view(), name='sync_unit'),
]