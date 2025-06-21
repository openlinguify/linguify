# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    # SEO Fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="Max 160 characters for SEO")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    
    # Content
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/images/', null=True, blank=True)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # SEO and engagement
    view_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=5, help_text="Estimated reading time in minutes")
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Calculate reading time (average 200 words per minute)
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at and self.published_at <= timezone.now()
    
    @property
    def comments_count(self):
        """Get total approved comments count"""
        return self.comments.filter(is_approved=True).count()
    
    @property
    def views_count(self):
        """Alias for view_count to match template"""
        return self.view_count
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # New fields for enhanced functionality
    likes_count = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author_name} on {self.post.title}'
    
    @property
    def depth(self):
        """Calculate comment depth for nested display"""
        if not self.parent:
            return 0
        return self.parent.depth + 1
    
    def get_replies(self):
        """Get approved replies for this comment"""
        return self.replies.filter(is_approved=True).order_by('created_at')


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'author_email']
        indexes = [
            models.Index(fields=['comment']),
        ]
    
    def __str__(self):
        return f'{self.author_name} likes comment on {self.comment.post.title}'


class CommentReport(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam or unwanted commercial content'),
        ('harassment', 'Harassment or bullying'),
        ('hate_speech', 'Hate speech or discrimination'),
        ('inappropriate', 'Inappropriate or offensive content'),
        ('misinformation', 'False or misleading information'),
        ('copyright', 'Copyright violation'),
        ('other', 'Other (please specify)')
    ]
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    reporter_name = models.CharField(max_length=100)
    reporter_email = models.EmailField()
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    additional_info = models.TextField(blank=True, help_text="Additional details about the report")
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    moderator_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['comment', 'reporter_email', 'reason']
        indexes = [
            models.Index(fields=['comment']),
            models.Index(fields=['is_reviewed']),
        ]
    
    def __str__(self):
        return f'Report: {self.get_reason_display()} on comment by {self.comment.author_name}'


class ProfanityWord(models.Model):
    """
    Secure storage for profanity words across multiple languages
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('nl', 'Dutch'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    word = models.CharField(max_length=100, db_index=True)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='mild')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['word', 'language']
        indexes = [
            models.Index(fields=['word', 'language']),
            models.Index(fields=['is_active']),
            models.Index(fields=['severity']),
        ]
        verbose_name = 'Profanity Word'
        verbose_name_plural = 'Profanity Words'
    
    def __str__(self):
        return f'{self.word} ({self.get_language_display()}) - {self.get_severity_display()}'