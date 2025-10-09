from django.urls import path
from .views import DocumentUploadView, process_document, get_upload_status

app_name = 'ai_documents'

urlpatterns = [
    path('', DocumentUploadView.as_view(), name='upload'),
    path('process/', process_document, name='process_document'),
    path('status/<int:upload_id>/', get_upload_status, name='upload_status'),
]
