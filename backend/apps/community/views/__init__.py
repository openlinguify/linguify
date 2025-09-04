"""
Community views
"""
from .community_settings_views import CommunitySettingsView
from .community_views import (
    CommunityMainView,
    DiscoverUsersView,
    FriendsListView,
    FriendRequestsView,
    ActivityFeedView,
    UserProfileView,
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
)
from .community_group_views import (
    GroupsView,
    GroupDetailView,
    GroupManageView,
    create_group,
    send_group_message,
    get_group_messages,
    promote_to_moderator,
    remove_moderator,
    remove_group_member,
    update_group_settings,
    delete_group,
)

__all__ = [
    'CommunitySettingsView',
    'CommunityMainView',
    'DiscoverUsersView',
    'FriendsListView',
    'FriendRequestsView',
    'GroupsView',
    'GroupDetailView',
    'GroupManageView',
    'ActivityFeedView',
    'UserProfileView',
    'send_friend_request',
    'accept_friend_request',
    'reject_friend_request',
    'create_group',
    'send_group_message',
    'get_group_messages',
    'promote_to_moderator',
    'remove_moderator',
    'remove_group_member',
    'update_group_settings',
    'delete_group',
]