from django.urls import path
from . import views

urlpatterns = [
    path('delete-account/', views.delete_account, name='delete_account'),
    path('upload-profile-photo/', views.UploadProfilePhotoView.as_view(), name='upload_profile_photo'),
    ]
