# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from .models import BlogPost, Category, Tag, Comment, CommentLike, CommentReport, ProfanityWord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = 'Posts'


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author_name', 'author_email', 'content', 'is_approved']
    readonly_fields = ['author_name', 'author_email', 'content', 'created_at']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'view_count', 'reading_time']
    list_filter = ['status', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ['collapse']
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'reading_time')
        }),
        ('Stats', {
            'fields': ('view_count',),
            'classes': ['collapse']
        })
    )
    
    readonly_fields = ['view_count']
    inlines = [CommentInline]
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')
    
    actions = ['make_published', 'make_draft']
    
    def make_published(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, f"{queryset.count()} posts were successfully published.")
    make_published.short_description = "Mark selected posts as published"
    
    def make_draft(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f"{queryset.count()} posts were moved to draft.")
    make_draft.short_description = "Mark selected posts as draft"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author_name', 'author_email', 'created_at', 'is_approved', 'likes_count', 'parent']
    list_filter = ['is_approved', 'created_at', 'post', 'parent']
    search_fields = ['author_name', 'author_email', 'content']
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} comments were approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} comments were disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'author_name', 'author_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author_name', 'author_email', 'comment__content']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comment', 'comment__post')


@admin.register(ProfanityWord)
class ProfanityWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'language', 'severity', 'is_active', 'created_at']
    list_filter = ['language', 'severity', 'is_active', 'created_at']
    search_fields = ['word']
    actions = ['activate_words', 'deactivate_words', 'set_mild', 'set_moderate', 'set_severe']
    list_per_page = 50
    
    fieldsets = (
        ('Word Information', {
            'fields': ('word', 'language', 'severity', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def activate_words(self, request, queryset):
        queryset.update(is_active=True)
        # Clear cache after changes
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        self.message_user(request, f"{queryset.count()} words were activated.")
    activate_words.short_description = "Activate selected words"
    
    def deactivate_words(self, request, queryset):
        queryset.update(is_active=False)
        # Clear cache after changes
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        self.message_user(request, f"{queryset.count()} words were deactivated.")
    deactivate_words.short_description = "Deactivate selected words"
    
    def set_mild(self, request, queryset):
        queryset.update(severity='mild')
        # Clear cache after changes
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        self.message_user(request, f"{queryset.count()} words were set to mild severity.")
    set_mild.short_description = "Set severity to Mild"
    
    def set_moderate(self, request, queryset):
        queryset.update(severity='moderate')
        # Clear cache after changes
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        self.message_user(request, f"{queryset.count()} words were set to moderate severity.")
    set_moderate.short_description = "Set severity to Moderate"
    
    def set_severe(self, request, queryset):
        queryset.update(severity='severe')
        # Clear cache after changes
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        self.message_user(request, f"{queryset.count()} words were set to severe severity.")
    set_severe.short_description = "Set severity to Severe"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Clear cache when individual words are saved
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # Clear cache when words are deleted
        from .profanity_filter import profanity_filter
        profanity_filter.clear_cache()
    
    class Meta:
        verbose_name = 'Profanity Word'
        verbose_name_plural = 'Profanity Words'


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ['report_summary', 'blog_post', 'comment_preview', 'reporter_name', 'reason', 'created_at', 'is_reviewed']
    list_filter = ['reason', 'is_reviewed', 'created_at', 'comment__post']
    search_fields = ['reporter_name', 'reporter_email', 'comment__content', 'additional_info', 'comment__post__title', 'comment__author_name']
    actions = ['mark_reviewed', 'mark_unreviewed']
    
    fieldsets = (
        ('Context Information', {
            'fields': ('blog_post_link', 'comment_details', 'comment_content_display'),
            'description': 'Information about the reported content'
        }),
        ('Report Information', {
            'fields': ('reporter_name', 'reporter_email', 'reason', 'created_at'),
        }),
        ('Additional Details', {
            'fields': ('additional_info',),
            'classes': ['collapse']
        }),
        ('Moderation Actions', {
            'fields': ('is_reviewed', 'moderator_notes'),
            'classes': ['wide']
        })
    )
    
    readonly_fields = ['blog_post_link', 'comment_details', 'comment_content_display', 'created_at']
    
    def report_summary(self, obj):
        """Concise report summary for list view"""
        return f"Report #{obj.id}: {obj.get_reason_display()}"
    report_summary.short_description = 'Report'
    report_summary.admin_order_field = 'id'
    
    def blog_post(self, obj):
        """Display the blog post title for list view"""
        if obj.comment and obj.comment.post:
            return f"📄 {obj.comment.post.title[:50]}{'...' if len(obj.comment.post.title) > 50 else ''}"
        return '-'
    blog_post.short_description = 'Article'
    blog_post.admin_order_field = 'comment__post__title'
    
    def comment_preview(self, obj):
        """Show comment preview in list view"""
        if obj.comment:
            content = obj.comment.content[:60] + '...' if len(obj.comment.content) > 60 else obj.comment.content
            return f"💬 by {obj.comment.author_name}: {content}"
        return '-'
    comment_preview.short_description = 'Comment'
    
    def blog_post_link(self, obj):
        """Display blog post with clickable link"""
        if obj.comment and obj.comment.post:
            post = obj.comment.post
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<strong>📄 Article:</strong><br>'
                '<a href="/admin/blog/blogpost/{}/change/" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">'
                '{}</a><br>'
                '<small style="color: #666;">ID: {} | Author: {} | Views: {}</small>'
                '</div>',
                post.id, post.title, post.id, post.author.get_full_name() or post.author.username, post.view_count
            )
        return '-'
    blog_post_link.short_description = 'Related Article'
    
    def comment_details(self, obj):
        """Display detailed comment information with link"""
        if obj.comment:
            comment = obj.comment
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<strong>💬 Comment Details:</strong><br>'
                '<a href="/admin/blog/comment/{}/change/" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">'
                'Comment ID: {} by {}</a><br>'
                '<small style="color: #666;">Email: {} | Posted: {} | Likes: {} | Approved: {}</small>'
                '</div>',
                comment.id, comment.id, comment.author_name, 
                comment.author_email, comment.created_at.strftime('%Y-%m-%d %H:%M'),
                comment.likes_count, '✅' if comment.is_approved else '❌'
            )
        return '-'
    comment_details.short_description = 'Comment Information'
    
    def comment_content_display(self, obj):
        """Display the actual comment content"""
        if obj.comment:
            content = obj.comment.content
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; border-radius: 4px; margin-top: 10px;">'
                '<strong>🚨 Reported Comment Content:</strong><br><br>'
                '<div style="font-style: italic; line-height: 1.5;">{}</div>'
                '</div>',
                content.replace('\n', '<br>')
            )
        return '-'
    comment_content_display.short_description = 'Reported Content'
    
    def mark_reviewed(self, request, queryset):
        queryset.update(is_reviewed=True)
        self.message_user(request, f"{queryset.count()} reports were marked as reviewed.")
    mark_reviewed.short_description = "Mark selected reports as reviewed"
    
    def mark_unreviewed(self, request, queryset):
        queryset.update(is_reviewed=False)
        self.message_user(request, f"{queryset.count()} reports were marked as unreviewed.")
    mark_unreviewed.short_description = "Mark selected reports as unreviewed"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comment', 'comment__post')


