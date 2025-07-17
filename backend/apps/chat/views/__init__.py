# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from .chat_settings_views import ChatSettingsView

# Import all views from the main_views.py file
import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the main views module
import main_views

# Make all main views available
chat_redirect = main_views.chat_redirect
get_conversations = main_views.get_conversations
get_messages = main_views.get_messages
start_conversation = main_views.start_conversation
search_users = main_views.search_users
send_message = main_views.send_message
call_test_page = main_views.call_test_page
debug_calls_page = main_views.debug_calls_page