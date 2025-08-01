"""
API views for SaaS functionality.
"""
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from apps.notification.models import Notification
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


@method_decorator(login_required, name='dispatch')
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
        try:
            # Get all recent notifications (read and unread) for display
            all_notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]
            
            # Count only unread notifications
            unread_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            
            data = {
                'unread_count': unread_count,
                'notifications': [
                    {
                        'id': str(notif.id),
                        'title': notif.title,
                        'message': notif.message,
                        'type': notif.type,
                        'icon': self._get_notification_icon(notif.type),
                        'color': self._get_notification_color(notif.type),
                        'time': notif.created_at.strftime('%H:%M'),
                        'priority': notif.priority,
                        'data': notif.data or {},
                        'is_read': notif.is_read,
                    }
                    for notif in all_notifications
                ]
            }
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error getting notifications for user {request.user.id}: {e}")
            return JsonResponse({
                'unread_count': 0,
                'notifications': []
            })
    
    def _get_notification_icon(self, notification_type):
        """Get Bootstrap icon for notification type"""
        return self.NOTIFICATION_ICONS.get(notification_type, 'bi-bell')
    
    def post(self, request):
        """Handle marking notifications as read"""
        try:
            action = request.POST.get('action')
            
            if action == 'mark_read':
                notification_id = request.POST.get('notification_id')
                if notification_id:
                    notification = Notification.objects.filter(
                        id=notification_id, 
                        user=request.user
                    ).first()
                    if notification:
                        notification.is_read = True
                        notification.save()
                        return JsonResponse({'success': True})
                    else:
                        return JsonResponse({'success': False, 'error': 'Notification not found'})
                        
            elif action == 'mark_all_read':
                Notification.objects.filter(
                    user=request.user,
                    is_read=False
                ).update(is_read=True)
                return JsonResponse({'success': True})
                
            return JsonResponse({'success': False, 'error': 'Invalid action'})
            
        except Exception as e:
            logger.error(f"Error handling notification action: {e}")
            return JsonResponse({'success': False, 'error': 'Server error'})
    
    def _get_notification_icon(self, notification_type):
        """Get Bootstrap icon for notification type"""
        return self.NOTIFICATION_ICONS.get(notification_type, 'bi-bell')
    
    def _get_notification_color(self, notification_type):
        """Get color class for notification type"""
        return self.NOTIFICATION_COLORS.get(notification_type, 'primary')