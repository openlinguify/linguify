# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import re
import json
import logging
import hashlib
from django.utils.html import escape
from django.core.cache import cache
from .models import BlogPost, Category, Tag, Comment, CommentLike, CommentReport
from .profanity_filter import validate_comment_content

# Setup logging
logger = logging.getLogger(__name__)

# Custom logging formatters
class BlogViewLogger:
    """Custom logger for blog views with structured logging"""
    
    @staticmethod
    def log_view_attempt(request, post_id, post_title, result='success'):
        """Log view counting attempts with context"""
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                  request.META.get('REMOTE_ADDR', 'unknown'))
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')[:100]
        
        extra = {
            'post_id': post_id,
            'post_title': post_title,
            'user_ip': user_ip,
            'user_agent': user_agent,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }
        
        if result == 'success':
            logger.info(f"👁️ View counted - Post: '{post_title}' (ID: {post_id}) | IP: {user_ip}", extra=extra)
        elif result == 'duplicate':
            logger.debug(f"👁️ Duplicate view - Post: '{post_title}' (ID: {post_id}) | IP: {user_ip}", extra=extra)
        else:
            logger.warning(f"👁️ View attempt failed - Post: '{post_title}' (ID: {post_id}) | IP: {user_ip} | Error: {result}", extra=extra)
    
    @staticmethod
    def log_error(operation, error, request=None, extra_context=None):
        """Log errors with context"""
        context = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': timezone.now().isoformat()
        }
        
        if request:
            context['user_ip'] = request.META.get('HTTP_X_FORWARDED_FOR', 
                                                request.META.get('REMOTE_ADDR', 'unknown'))
            context['method'] = request.method
            context['path'] = request.path
        
        if extra_context:
            context.update(extra_context)
            
        logger.error(f"💥 {operation} failed: {error}", extra=context, exc_info=True)


class SecurityUtils:
    """Security utilities for blog operations"""
    
    @staticmethod
    def get_client_ip(request):
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    @staticmethod
    def is_rate_limited(request, action, limit=5, window=300):
        """Check if user is rate limited for specific action"""
        ip = SecurityUtils.get_client_ip(request)
        cache_key = f"rate_limit_{action}_{ip}"
        
        current_count = cache.get(cache_key, 0)
        if current_count >= limit:
            return True
        
        cache.set(cache_key, current_count + 1, window)
        return False
    
    @staticmethod
    def sanitize_input(text, max_length=None):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Escape HTML
        text = escape(text)
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def detect_spam_patterns(content):
        """Enhanced spam detection"""
        spam_patterns = [
            r'http[s]?://[^\s]+',  # URLs
            r'www\.[^\s]+',        # Websites
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'buy\s+now',          # Commercial phrases
            r'click\s+here',
            r'free\s+money',
            r'earn\s+\$\d+',
            r'viagra|cialis',      # Pharmacy spam
            r'casino|poker',       # Gambling spam
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def generate_content_hash(content, author_email):
        """Generate hash for duplicate detection"""
        combined = f"{content.lower().strip()}{author_email.lower()}"
        return hashlib.sha256(combined.encode()).hexdigest()


class CommentValidator:
    """Enhanced comment validation"""
    
    @staticmethod
    def validate_comment_data(data, request):
        """Comprehensive comment validation"""
        errors = []
        
        # Extract and sanitize data
        author_name = SecurityUtils.sanitize_input(data.get('author_name', ''), 100)
        author_email = SecurityUtils.sanitize_input(data.get('author_email', ''), 254)
        content = SecurityUtils.sanitize_input(data.get('content', ''), 1000)
        
        # Rate limiting
        if SecurityUtils.is_rate_limited(request, 'comment_submission', limit=3, window=300):
            errors.append('Too many comments submitted. Please wait before posting again.')
        
        # Basic validation
        if not author_name or len(author_name) < 2:
            errors.append('Name must be at least 2 characters long.')
        
        if not author_email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(author_email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        if not content or len(content) < 10:
            errors.append('Comment must be at least 10 characters long.')
        
        # Spam detection
        if SecurityUtils.detect_spam_patterns(content):
            errors.append('Your comment contains unauthorized content.')
            BlogViewLogger.log_error('spam_detected', 
                                   Exception('Spam pattern detected'), 
                                   request,
                                   {'content_preview': content[:50], 'author_email': author_email})
        
        # Duplicate detection
        content_hash = SecurityUtils.generate_content_hash(content, author_email)
        cache_key = f"comment_hash_{content_hash}"
        if cache.get(cache_key):
            errors.append('This comment appears to be a duplicate.')
        else:
            cache.set(cache_key, True, 3600)  # 1 hour
        
        return {
            'errors': errors,
            'cleaned_data': {
                'author_name': author_name,
                'author_email': author_email,
                'content': content
            }
        }


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list_enhanced.html'  # Use the new enhanced template
    context_object_name = 'posts'
    paginate_by = 8  # Increased for better layout
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags', 'comments')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(meta_keywords__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Tag filter
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Special filters (Odoo-style)
        if self.request.GET.get('featured'):
            queryset = queryset.filter(view_count__gte=100)  # Featured = high views
        elif self.request.GET.get('recent'):
            queryset = queryset.filter(published_at__gte=timezone.now() - timezone.timedelta(days=30))
        elif self.request.GET.get('commented'):
            # Get posts with most comments
            from django.db.models import Count
            queryset = queryset.annotate(
                comment_count=Count('comments', filter=Q(comments__is_approved=True))
            ).filter(comment_count__gte=1).order_by('-comment_count')
        
        # Sorting (Odoo-style)
        sort_by = self.request.GET.get('sort', 'newest')
        if sort_by == 'popular':
            queryset = queryset.order_by('-view_count', '-published_at')
        elif sort_by == 'comments':
            from django.db.models import Count
            queryset = queryset.annotate(
                comment_count=Count('comments', filter=Q(comments__is_approved=True))
            ).order_by('-comment_count', '-published_at')
        else:  # newest (default)
            queryset = queryset.order_by('-published_at')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Use caching for expensive operations
        context.update(self._get_cached_context_data())
        
        # Keep existing context
        context['search_query'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_tag'] = self.request.GET.get('tag', '')
        
        return context
    
    def _get_cached_context_data(self):
        """Get context data with caching for performance"""
        cache_key = 'blog_context_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            from django.db.models import Count, Sum
            
            # Categories with post counts
            categories = Category.objects.annotate(
                posts_count=Count('blogpost', filter=Q(blogpost__status='published'))
            ).order_by('name')
            
            # Popular tags (most used)
            popular_tags = Tag.objects.annotate(
                posts_count=Count('blogpost', filter=Q(blogpost__status='published'))
            ).filter(posts_count__gt=0).order_by('-posts_count')[:12]
            
            # Statistics for sidebar (single query optimization)
            published_posts = BlogPost.objects.filter(status='published')
            
            # Use aggregation to get all stats in one query
            stats = published_posts.aggregate(
                total_posts=Count('id'),
                total_views=Sum('view_count'),
                featured_count=Count('id', filter=Q(view_count__gte=100)),
                recent_count=Count('id', filter=Q(
                    published_at__gte=timezone.now() - timezone.timedelta(days=30)
                ))
            )
            
            # Separate query for comments (different model)
            total_comments = Comment.objects.filter(is_approved=True).count()
            
            # Commented posts count
            commented_count = published_posts.annotate(
                comment_count=Count('comments', filter=Q(comments__is_approved=True))
            ).filter(comment_count__gte=1).count()
            
            context_data = {
                'categories': categories,
                'popular_tags': popular_tags,
                'total_posts': stats['total_posts'] or 0,
                'total_comments': total_comments,
                'total_views': stats['total_views'] or 0,
                'featured_count': stats['featured_count'] or 0,
                'recent_count': stats['recent_count'] or 0,
                'commented_count': commented_count,
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, context_data, 300)
            return context_data
            
        except Exception as e:
            BlogViewLogger.log_error('context_data_generation', e, None)
            # Return minimal context if error
            return {
                'categories': [],
                'popular_tags': [],
                'total_posts': 0,
                'total_comments': 0,
                'total_views': 0,
                'featured_count': 0,
                'recent_count': 0,
                'commented_count': 0,
            }


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags', 'comments')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Increment view count on GET requests with enhanced error handling
        if self.request.method == 'GET':
            self._handle_view_counting(obj)
        
        return obj
    
    def _handle_view_counting(self, post):
        """Handle view counting with comprehensive error handling"""
        try:
            # Validate post object
            if not post or not hasattr(post, 'pk') or not post.pk:
                BlogViewLogger.log_error('view_counting', 
                                       Exception('Invalid post object'), 
                                       self.request,
                                       {'post_id': getattr(post, 'pk', 'unknown')})
                return
            
            # Anti-spam check with cookie and cache-based rate limiting
            cookie_name = f'viewed_{post.pk}'
            last_viewed = self.request.COOKIES.get(cookie_name)
            
            # Additional cache-based check to prevent race conditions
            ip_address = SecurityUtils.get_client_ip(self.request)
            cache_key = f"view_counted_{post.pk}_{ip_address}"
            
            if last_viewed or cache.get(cache_key):
                BlogViewLogger.log_view_attempt(self.request, post.pk, post.title, 'duplicate')
                return
            
            # Set cache immediately to prevent race conditions
            cache.set(cache_key, True, 300)  # 5 minutes
            
            # Attempt to increment view count with atomic operation
            try:
                updated_rows = BlogPost.objects.filter(
                    pk=post.pk,
                    status='published'  # Additional safety check
                ).update(view_count=F('view_count') + 1)
                
                if updated_rows == 1:
                    BlogViewLogger.log_view_attempt(self.request, post.pk, post.title, 'success')
                    # Set cookie for anti-spam
                    self.view_cookie_to_set = (cookie_name, 'viewed')
                else:
                    BlogViewLogger.log_view_attempt(self.request, post.pk, post.title, 'no_update')
                    
            except Exception as db_error:
                BlogViewLogger.log_error('database_update', db_error, self.request, {
                    'post_id': post.pk,
                    'post_title': post.title,
                    'operation': 'view_count_increment'
                })
                
        except Exception as general_error:
            BlogViewLogger.log_error('view_counting_general', general_error, self.request, {
                'post_id': getattr(post, 'pk', 'unknown'),
                'post_title': getattr(post, 'title', 'unknown')
            })
    
    def get(self, request, *args, **kwargs):
        """Override get to set the anti-spam cookie with error handling"""
        try:
            response = super().get(request, *args, **kwargs)
            
            # Set the view cookie if needed
            if hasattr(self, 'view_cookie_to_set'):
                try:
                    cookie_name, cookie_value = self.view_cookie_to_set
                    response.set_cookie(
                        cookie_name, 
                        cookie_value, 
                        max_age=10,  # 10 seconds
                        httponly=True,  # Security: prevent XSS
                        samesite='Lax'  # Security: CSRF protection
                    )
                except Exception as cookie_error:
                    BlogViewLogger.log_error('cookie_setting', cookie_error, request, {
                        'cookie_data': getattr(self, 'view_cookie_to_set', 'unknown')
                    })
            
            return response
            
        except Exception as view_error:
            BlogViewLogger.log_error('blog_detail_view', view_error, request, {
                'view_name': 'BlogDetailView',
                'kwargs': kwargs
            })
            
            # Fallback: try to render a basic error page or redirect
            try:
                from django.shortcuts import render
                return render(request, 'blog/error.html', {
                    'error_message': 'Sorry, there was an error loading this article.',
                    'error_code': 'VIEW_ERROR'
                }, status=500)
            except:
                # Last resort: redirect to blog list
                from django.shortcuts import redirect
                return redirect('blog:list')
    
    def post(self, request, *args, **kwargs):
        """Handle comment submission"""
        post = self.get_object()
        
        # Get form data
        author_name = request.POST.get('author_name', '').strip()
        author_email = request.POST.get('author_email', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        # Validation errors list
        errors = []
        
        # Basic validation
        if not author_name:
            errors.append('Name is required.')
        elif len(author_name) < 2:
            errors.append('Name must be at least 2 characters long.')
        elif len(author_name) > 100:
            errors.append('Name cannot exceed 100 characters.')
        
        if not author_email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(author_email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        if not content:
            errors.append('Comment is required.')
        elif len(content) < 10:
            errors.append('Comment must be at least 10 characters long.')
        elif len(content) > 1000:
            errors.append('Comment cannot exceed 1000 characters.')
        
        # Check for spam (basic protection)
        spam_patterns = [
            r'http[s]?://',  # URLs
            r'www\.',        # Websites
            r'\.com',        # .com domains
            r'buy now',      # Spam phrases
            r'click here',
        ]
        for pattern in spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append('Your comment contains unauthorized content.')
                break
        
        # Check for profanity and vulgar language - ZERO TOLERANCE
        profanity_result = validate_comment_content(content)
        if profanity_result['has_profanity']:
            # ANY profanity detected - block completely
            errors.append(profanity_result['warning_message'])
            # Log profanity attempt for admin review
            logger.warning(f"🚨 Profanity blocked - Severity: {profanity_result['severity']} | "
                         f"Words: {profanity_result['found_words']} | User: {author_name} | Email: {author_email}")
        
        # Check parent comment if provided
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post, is_approved=True)
            except Comment.DoesNotExist:
                errors.append('The parent comment does not exist or is not approved.')
        
        # If there are validation errors, display them and return
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('blog:post_detail', slug=post.slug)
        
        try:
            # Create comment
            comment = Comment.objects.create(
                post=post,
                author_name=author_name,
                author_email=author_email,
                content=content,
                parent=parent,
                is_approved=True  # Auto-approve comments without profanity
            )
            
            messages.success(request, 'Your comment has been posted successfully!')
            
        except Exception as e:
            messages.error(request, 'An error occurred while submitting your comment. Please try again.')
        
        return redirect('blog:post_detail', slug=post.slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Related posts
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).exclude(pk=post.pk).filter(
            Q(category=post.category) | Q(tags__in=post.tags.all())
        ).distinct()[:3]
        
        # Comments (approved only)
        context['comments'] = post.comments.filter(is_approved=True, parent=None).order_by('created_at')
        
        return context


def blog_category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author').prefetch_related('tags')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_category.html', context)


def blog_tag_view(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(
        tags=tag,
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category')
    
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_tag.html', context)


@csrf_protect
def comment_like_toggle(request):
    """Toggle like on a comment via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
        
    logger.info(f"👍 Like toggle request from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # Parse request data
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        author_name = data.get('author_name', '').strip()
        author_email = data.get('author_email', '').strip()
        
        logger.info(f"📤 Like request data: comment_id={comment_id}, name={author_name}, email={author_email}")
        
        # Rate limiting check
        if SecurityUtils.is_rate_limited(request, 'comment_like', limit=10, window=60):
            return JsonResponse({'error': 'Too many like actions. Please wait.'}, status=429)
        
        if not all([comment_id, author_name, author_email]):
            logger.warning(f"❌ Missing required fields: comment_id={comment_id}, name={bool(author_name)}, email={bool(author_email)}")
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Validate email
        try:
            validate_email(author_email)
            logger.debug(f"✅ Email validation passed: {author_email}")
        except ValidationError:
            logger.warning(f"❌ Invalid email address: {author_email}")
            return JsonResponse({'error': 'Invalid email address'}, status=400)
        
        # Get comment
        try:
            comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
            logger.info(f"📄 Found comment {comment_id} by {comment.author_name}")
        except Exception as e:
            logger.error(f"❌ Comment not found: {comment_id}, error: {e}")
            return JsonResponse({'error': 'Comment not found'}, status=404)
        
        # Check if user already liked this comment
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            author_email=author_email,
            defaults={'author_name': author_name}
        )
        
        if created:
            # User liked the comment
            Comment.objects.filter(id=comment_id).update(likes_count=F('likes_count') + 1)
            liked = True
            logger.info(f"❤️ User {author_email} liked comment {comment_id}")
        else:
            # User unliked the comment
            like.delete()
            Comment.objects.filter(id=comment_id).update(likes_count=F('likes_count') - 1)
            liked = False
            logger.info(f"💔 User {author_email} unliked comment {comment_id}")
        
        # Get updated count
        comment.refresh_from_db()
        new_count = comment.likes_count
        
        logger.info(f"📊 Updated like count for comment {comment_id}: {new_count}")
        
        response_data = {
            'success': True,
            'liked': liked,
            'likes_count': new_count
        }
        logger.info(f"📤 Sending response: {response_data}")
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"💥 Unexpected error in comment_like_toggle: {e}", exc_info=True)
        return JsonResponse({'error': 'An error occurred'}, status=500)


@csrf_protect
def comment_report(request):
    """Report a comment via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        reporter_name = data.get('reporter_name', '').strip()
        reporter_email = data.get('reporter_email', '').strip()
        reason = data.get('reason', '').strip()
        additional_info = data.get('additional_info', '').strip()
        
        # Basic validation for reports (different from comments)
        if not reporter_name or len(reporter_name) < 2:
            return JsonResponse({'error': 'Reporter name must be at least 2 characters'}, status=400)
        
        if not reporter_email:
            return JsonResponse({'error': 'Reporter email is required'}, status=400)
        
        # Rate limiting for reports
        if SecurityUtils.is_rate_limited(request, 'comment_report', limit=3, window=300):
            return JsonResponse({'error': 'Too many reports submitted. Please wait before reporting again.'}, status=429)
        
        if not all([comment_id, reporter_name, reporter_email, reason]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Validate reason
        valid_reasons = [choice[0] for choice in CommentReport.REPORT_REASONS]
        if reason not in valid_reasons:
            return JsonResponse({'error': 'Invalid report reason'}, status=400)
        
        comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
        
        # Check if user already reported this comment for this reason
        report, created = CommentReport.objects.get_or_create(
            comment=comment,
            reporter_email=reporter_email,
            reason=reason,
            defaults={
                'reporter_name': reporter_name,
                'additional_info': additional_info
            }
        )
        
        if created:
            BlogViewLogger.log_view_attempt(request, comment_id, f"Report: {reason}", 'success')
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your report. Our moderators will review it shortly.'
            })
        else:
            return JsonResponse({
                'error': 'You have already reported this comment for this reason.'
            }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        BlogViewLogger.log_error('comment_report', e, request, {
            'comment_id': comment_id if 'comment_id' in locals() else 'unknown'
        })
        return JsonResponse({'error': 'An error occurred while submitting your report'}, status=500)


@csrf_protect
def reply_to_comment(request, comment_id):
    """Handle replies to specific comments"""
    logger.info(f"💬 Reply request to comment {comment_id} from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        parent_comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
        logger.info(f"📄 Found parent comment {comment_id} by {parent_comment.author_name}")
    except Exception as e:
        logger.error(f"❌ Parent comment {comment_id} not found: {e}")
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Parent comment not found.'
            }, status=404)
        else:
            messages.error(request, 'Parent comment not found.')
            return redirect('blog:list')
    
    if request.method == 'POST':
        # Get form data
        author_name = request.POST.get('author_name', '').strip()
        author_email = request.POST.get('author_email', '').strip()
        content = request.POST.get('content', '').strip()
        
        logger.info(f"📤 Reply data: name={author_name}, email={author_email}, content_length={len(content)}")
        
        # Validation (reuse existing validation logic)
        errors = []
        
        if not author_name:
            errors.append('Name is required.')
        elif len(author_name) < 2:
            errors.append('Name must be at least 2 characters long.')
        elif len(author_name) > 100:
            errors.append('Name cannot exceed 100 characters.')
        
        if not author_email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(author_email)
                logger.debug(f"✅ Email validation passed for reply: {author_email}")
            except ValidationError:
                errors.append('Please enter a valid email address.')
                logger.warning(f"❌ Invalid email in reply: {author_email}")
        
        if not content:
            errors.append('Comment is required.')
        elif len(content) < 10:
            errors.append('Comment must be at least 10 characters long.')
        elif len(content) > 1000:
            errors.append('Comment cannot exceed 1000 characters.')
        
        # Prevent deep nesting (limit to 3 levels)
        if parent_comment.depth >= 2:
            errors.append('Maximum reply depth reached.')
            logger.warning(f"❌ Reply depth limit reached for comment {comment_id}, current depth: {parent_comment.depth}")
        
        # Check for profanity and vulgar language in replies - ZERO TOLERANCE
        profanity_result = validate_comment_content(content)
        if profanity_result['has_profanity']:
            # ANY profanity detected - block completely
            errors.append(profanity_result['warning_message'])
            # Log profanity attempt for admin review
            logger.warning(f"🚨 Profanity blocked in reply - Severity: {profanity_result['severity']} | "
                         f"Words: {profanity_result['found_words']} | User: {author_name} | Email: {author_email}")
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
        
        if errors:
            logger.warning(f"❌ Reply validation failed: {errors}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': errors[0] if errors else 'Validation failed'
                }, status=400)
            else:
                for error in errors:
                    messages.error(request, error)
        else:
            try:
                reply = Comment.objects.create(
                    post=parent_comment.post,
                    author_name=author_name,
                    author_email=author_email,
                    content=content,
                    parent=parent_comment,
                    is_approved=True  # Auto-approve replies without profanity
                )
                logger.info(f"✅ Reply created successfully: ID={reply.id}, parent={comment_id}, author={author_name}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Your reply has been posted successfully!',
                        'reply_id': reply.id
                    })
                else:
                    messages.success(request, 'Your reply has been posted successfully!')
            except Exception as e:
                logger.error(f"💥 Error creating reply: {e}", exc_info=True)
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'An error occurred while submitting your reply. Please try again.'
                    }, status=500)
                else:
                    messages.error(request, 'An error occurred while submitting your reply. Please try again.')
        
        # For non-AJAX requests, redirect back to the blog post
        if not is_ajax:
            blog_post_url = request.build_absolute_uri(parent_comment.post.get_absolute_url())
            logger.info(f"🔄 Redirecting to: {blog_post_url}")
            return redirect('blog:post_detail', slug=parent_comment.post.slug)
    
    # GET request - not allowed for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'GET method not allowed for AJAX reply requests'
        }, status=405)
    
    # GET request - show reply form (for non-AJAX)
    logger.info(f"📝 Showing reply form for comment {comment_id}")
    context = {
        'parent_comment': parent_comment,
        'post': parent_comment.post,
        'blog_post_url': request.build_absolute_uri(parent_comment.post.get_absolute_url())
    }
    return render(request, 'blog/comment_reply.html', context)