"""
Admin Dashboard for User Statistics
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Import through ORM to avoid circular imports
from django.apps import apps
try:
    CoachProfile = apps.get_model('authentication', 'CoachProfile')
    Review = apps.get_model('authentication', 'Review')
except:
    # Fallback if models aren't registered yet
    CoachProfile = None
    Review = None

class UserStatsDashboard(TemplateView):
    template_name = 'admin/user_stats_dashboard.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # If models aren't available, return basic context
        if CoachProfile is None or Review is None:
            context.update({
                'title': 'User Statistics Dashboard',
                'model_error': True,
                'error_message': 'Unable to load required models. Make sure the app is properly installed.'
            })
            return context
            
        now = timezone.now()
        
        # Time ranges
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        coaches = User.objects.filter(is_coach=True).count()
        
        # User growth over time
        users_today = User.objects.filter(created_at__date=today).count()
        users_yesterday = User.objects.filter(created_at__date=yesterday).count()
        users_last_week = User.objects.filter(created_at__date__gte=week_ago).count()
        users_last_month = User.objects.filter(created_at__date__gte=month_ago).count()
        
        # Calculate growth rate safely
        previous_week_users = User.objects.filter(
            created_at__date__gte=week_ago - timedelta(days=7),
            created_at__date__lt=week_ago
        ).count()
        
        user_growth_rate = 0
        if previous_week_users > 0:
            user_growth_rate = ((users_last_week - previous_week_users) / previous_week_users) * 100
        
        # Login activity
        active_today = User.objects.filter(last_login__date=today).count()
        active_this_week = User.objects.filter(last_login__date__gte=week_ago).count()
        active_this_month = User.objects.filter(last_login__date__gte=month_ago).count()
        
        # Language distribution
        language_distribution = User.objects.values('target_language').annotate(
            total=Count('target_language')
        ).order_by('-total')[:5]
        
        if language_distribution:
            for lang in language_distribution:
                lang['percentage'] = (lang['total'] / total_users * 100) if total_users > 0 else 0
        
        # Level distribution
        level_distribution = User.objects.values('language_level').annotate(
            total=Count('language_level')
        ).order_by('language_level')
        
        if level_distribution:
            for level in level_distribution:
                level['percentage'] = (level['total'] / total_users * 100) if total_users > 0 else 0
        
        # Coach statistics
        avg_coach_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        coach_language_distribution = CoachProfile.objects.values('coaching_languages').annotate(
            total=Count('coaching_languages')
        ).order_by('-total')
        
        # Deletion statistics
        pending_deletion = User.objects.filter(is_pending_deletion=True).count()
        deletion_within_week = User.objects.filter(
            is_pending_deletion=True,
            deletion_date__lte=now + timedelta(days=7)
        ).count()
        
        # Profile completion stats
        users_with_complete_profiles = User.objects.exclude(
            Q(profile_picture='') | Q(profile_picture__isnull=True) |
            Q(bio='') | Q(bio__isnull=True) |
            Q(first_name='') | Q(last_name='') |
            Q(birthday__isnull=True)
        ).count()
        
        profile_completion_rate = (users_with_complete_profiles / total_users * 100) if total_users > 0 else 0
        
        context.update({
            'title': 'User Statistics Dashboard',
            'total_users': total_users,
            'active_users': active_users,
            'coaches': coaches,
            
            'users_today': users_today,
            'users_yesterday': users_yesterday,
            'users_last_week': users_last_week,
            'users_last_month': users_last_month,
            'user_growth_rate': round(user_growth_rate, 1),
            
            'active_today': active_today,
            'active_this_week': active_this_week,
            'active_this_month': active_this_month,
            'active_rate': round((active_this_week / total_users * 100), 1) if total_users > 0 else 0,
            
            'language_distribution': language_distribution,
            'level_distribution': level_distribution,
            
            'avg_coach_rating': round(avg_coach_rating, 1),
            'coach_language_distribution': coach_language_distribution,
            
            'pending_deletion': pending_deletion,
            'deletion_within_week': deletion_within_week,
            
            'profile_completion_rate': round(profile_completion_rate, 1),
            'model_error': False,
        })
        
        return context