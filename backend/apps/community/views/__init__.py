"""
Community views
"""
from .community_settings_views import CommunitySettingsView
from .community_views import (
    CommunityMainView,
    DiscoverUsersView,
    FriendsListView,
    FriendRequestsView,
    GroupsView,
    ActivityFeedView,
    UserProfileView,
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
)

__all__ = [
    'CommunitySettingsView',
    'CommunityMainView',
    'DiscoverUsersView',
    'FriendsListView',
    'FriendRequestsView',
    'GroupsView',
    'ActivityFeedView',
    'UserProfileView',
    'send_friend_request',
    'accept_friend_request',
    'reject_friend_request',
]