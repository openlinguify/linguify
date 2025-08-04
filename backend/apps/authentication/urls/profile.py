"""
Profile-specific URLs
"""
from django.urls import path
from ..views.views import UserProfileView

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),  # /profile/
    path('<str:username>/', UserProfileView.as_view(), name='user_profile'),  # /u/username/
]