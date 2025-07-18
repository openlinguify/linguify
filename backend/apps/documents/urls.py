from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FolderViewSet, DocumentViewSet, DocumentShareViewSet, 
    DocumentVersionViewSet, DocumentCommentViewSet,
    DocumentListView, DocumentDetailView, DocumentCreateView, 
    DocumentEditView, DocumentDeleteView, document_editor,
    folder_list, document_share, main_view
)
from .views.logging_views import (
    log_client_event, get_client_metrics, report_bug, system_health
)

app_name = 'documents'

# API Router for REST endpoints
router = DefaultRouter()
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'shares', DocumentShareViewSet, basename='documentshare')
router.register(r'versions', DocumentVersionViewSet, basename='documentversion')
router.register(r'comments', DocumentCommentViewSet, basename='documentcomment')

# API URLs
api_urlpatterns = [
    path('api/v1/', include(router.urls)),
    # Logging and monitoring endpoints
    path('api/v1/logging/', log_client_event, name='log_client_event'),
    path('api/v1/metrics/', get_client_metrics, name='get_client_metrics'),
    path('api/v1/report-bug/', report_bug, name='report_bug'),
    path('api/v1/health/', system_health, name='system_health'),
]

# Web URLs
web_urlpatterns = [
    # Main dashboard
    path('', main_view, name='main'),
    
    # Document CRUD
    path('list/', DocumentListView.as_view(), name='document_list'),
    path('create/', DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', DocumentEditView.as_view(), name='document_edit'),
    path('<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
    
    # Advanced editor
    path('<int:pk>/editor/', document_editor, name='document_editor'),
    
    # Sharing
    path('<int:pk>/share/', document_share, name='document_share'),
    
    # Folders
    path('folders/', folder_list, name='folder_list'),
]

# Combined URL patterns
urlpatterns = api_urlpatterns + web_urlpatterns