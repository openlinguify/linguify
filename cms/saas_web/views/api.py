"""
API views for SaaS functionality.
"""
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# from apps.notification.models import Notification  # Not available in CMS project
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class UserStatsAPI(View):
    """API pour les statistiques utilisateur"""
    
    def get(self, request):
        # TODO: Implement real statistics gathering
        stats = {
            'lessons_completed': 0,  # Could get from course app
            'study_streak': 0,  # Could get from user profile
            'words_learned': 0,  # Could get from vocabulary tracking
            'minutes_today': 0,  # Could get from session tracking
        }
        return JsonResponse(stats)


@method_decorator([login_required, csrf_exempt], name='dispatch')
class NotificationAPI(View):
    """API pour les notifications"""
    
    # Notification icon mapping
    NOTIFICATION_ICONS = {
        'info': 'bi-info-circle',
        'success': 'bi-check-circle',
        'warning': 'bi-exclamation-triangle',
        'error': 'bi-x-circle',
        'lesson_reminder': 'bi-book',
        'flashcard': 'bi-cards',
        'streak': 'bi-fire',
        'achievement': 'bi-trophy',
        'system': 'bi-gear',
        'progress': 'bi-graph-up',
        'terms': 'bi-file-text',
    }
    
    # Notification color mapping
    NOTIFICATION_COLORS = {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
        'lesson_reminder': 'info',
        'flashcard': 'primary',
        'streak': 'warning',
        'achievement': 'success',
        'system': 'secondary',
        'progress': 'info',
        'terms': 'warning',
    }
    
    def get(self, request):
        # CMS project doesn't have notification app - return empty for now
        return JsonResponse({
            'unread_count': 0,
            'notifications': []
        })
    
    def _get_notification_icon(self, notification_type):
        """Get Bootstrap icon for notification type"""
        return self.NOTIFICATION_ICONS.get(notification_type, 'bi-bell')
    
    def post(self, request):
        """Handle marking notifications as read - Not implemented in CMS"""
        return JsonResponse({'success': False, 'error': 'Notifications not available in CMS'})
    
    def _get_notification_icon(self, notification_type):
        """Get Bootstrap icon for notification type"""
        return self.NOTIFICATION_ICONS.get(notification_type, 'bi-bell')
    
    def _get_notification_color(self, notification_type):
        """Get color class for notification type"""
        return self.NOTIFICATION_COLORS.get(notification_type, 'primary')