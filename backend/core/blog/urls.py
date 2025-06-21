# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='list'),
    path('post/<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('category/<slug:slug>/', views.blog_category_view, name='category'),
    path('tag/<slug:slug>/', views.blog_tag_view, name='tag'),
    
    # Comment interactions
    path('comment/like/', views.comment_like_toggle, name='comment_like'),
    path('comment/report/', views.comment_report, name='comment_report'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='comment_reply'),
]