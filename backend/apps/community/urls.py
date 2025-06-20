from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.CommunityMainView.as_view(), name='main'),
    path('discover/', views.DiscoverUsersView.as_view(), name='discover'),
    path('friends/', views.FriendsListView.as_view(), name='friends'),
    path('friends/requests/', views.FriendRequestsView.as_view(), name='friend_requests'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('groups/', views.GroupsView.as_view(), name='groups'),
    path('feed/', views.ActivityFeedView.as_view(), name='feed'),
]