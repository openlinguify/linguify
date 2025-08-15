from django.urls import path
from . import views, api_views
from .views import CommunitySettingsView

app_name = 'community'

urlpatterns = [
    path('', views.CommunityMainView.as_view(), name='main'),
    path('discover/', views.DiscoverUsersView.as_view(), name='discover'),
    path('friends/', views.FriendsListView.as_view(), name='friends'),
    path('friends/requests/', views.FriendRequestsView.as_view(), name='friend_requests'),
    path('groups/', views.GroupsView.as_view(), name='groups'),
    path('feed/', views.ActivityFeedView.as_view(), name='feed'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Friend management API endpoints
    path('api/send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('api/accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('api/reject-friend-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    
    # Messaging API endpoints
    path('api/conversations/', api_views.get_conversations, name='get_conversations'),
    path('api/conversations/start/', api_views.start_conversation, name='start_conversation'),
    path('api/conversations/<int:conversation_id>/messages/', api_views.get_conversation_messages, name='get_conversation_messages'),
    path('api/conversations/<int:conversation_id>/send/', api_views.send_message, name='send_message'),
    
    # Language exchange API endpoints
    path('api/language-partners/', api_views.get_language_partners, name='get_language_partners'),
    path('api/language-exchange/create-room/', api_views.create_language_exchange_room, name='create_language_exchange_room'),
    path('api/friend-suggestions/', api_views.get_friend_suggestions, name='get_friend_suggestions'),
    
    # Settings endpoint
    path('settings/', CommunitySettingsView.as_view(), name='community-settings'),
]