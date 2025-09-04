from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.cache import cache
from app_manager.mixins import SettingsContextMixin
from ..serializers import TodoSettingsSerializer, TodoUserPreferencesSerializer
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class TodoSettingsView(SettingsContextMixin, View):
    """Interface web pour les paramètres de todo"""
    
    def get(self, request):
        """Affiche la page des paramètres de todo"""
        try:
            # Utiliser le mixin pour générer le contexte standardisé
            context = self.get_settings_context(
                user=request.user,
                active_tab_id='todo',
                page_title='To-do',
                page_subtitle='Configurez vos paramètres de productivité et gestion de tâches'
            )
            
            return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in TodoSettingsView: {e}")
            # Fallback
            return render(request, 'saas_web/settings/settings.html', {
                'page_title': 'To-do',
                'page_subtitle': 'Erreur lors du chargement des paramètres'
            })
    
    def post(self, request):
        """Traite la sauvegarde des paramètres de todo"""
        try:
            # Récupérer le type de paramètre
            setting_type = request.POST.get('setting_type', 'general')
            
            # Préparer la réponse de succès
            success_data = {
                'success': True,
                'message': 'Paramètres todo mis à jour avec succès',
                'setting_type': setting_type
            }
            
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            if is_ajax:
                return JsonResponse(success_data)
            else:
                messages.success(request, 'Paramètres todo mis à jour avec succès')
                return redirect('saas_web:todo_settings')
            
        except Exception as e:
            logger.error(f"Error in TodoSettingsView POST: {e}")
            
            error_data = {
                'success': False,
                'message': 'Erreur lors de la sauvegarde des paramètres'
            }
            
            if is_ajax:
                return JsonResponse(error_data, status=500)
            else:
                messages.error(request, 'Erreur lors de la sauvegarde des paramètres')
                return redirect('saas_web:todo_settings')


class TodoSettingsAPI(APIView):
    """
    Get and update todo app settings
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current todo settings for the user"""
        user = request.user
        cache_key = f"todo_settings_{user.id}"
        
        # Try to get from cache first
        settings_data = cache.get(cache_key)
        
        if settings_data is None:
            # Default settings if not found
            settings_data = {
                # View preferences
                'default_project_view': 'list',
                'default_task_view': 'list',
                
                # Task settings
                'auto_archive_completed': False,
                'auto_archive_days': 30,
                'show_subtask_count': True,
                'show_progress_bars': True,
                
                # Notification settings
                'enable_reminders': True,
                'reminder_minutes_before': 15,
                'daily_digest': True,
                'daily_digest_time': '09:00:00',
                'overdue_notifications': True,
                
                # Productivity settings
                'enable_time_tracking': False,
                'pomodoro_timer': False,
                'pomodoro_duration': 25,
                'break_duration': 5,
                
                # Interface settings
                'theme': 'auto',
                'compact_mode': False,
                'show_completed_tasks': True,
                'quick_add_shortcut': True,
                
                # Default values
                'default_task_priority': 'medium',
                'default_reminder_time': '09:00:00',
                
                # Collaboration settings
                'allow_task_sharing': True,
                'allow_project_sharing': True,
                'public_templates': False,
                
                # Data settings
                'backup_frequency': 'weekly',
                'export_format': 'json',
            }
            
            # Cache for 1 hour
            cache.set(cache_key, settings_data, 3600)
        
        serializer = TodoSettingsSerializer(data=settings_data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(settings_data)
    
    def post(self, request):
        """Update todo settings"""
        user = request.user
        serializer = TodoSettingsSerializer(data=request.data)
        
        if serializer.is_valid():
            settings_data = serializer.validated_data
            
            # Save to cache
            cache_key = f"todo_settings_{user.id}"
            cache.set(cache_key, settings_data, 3600)
            
            # Here you could also save to database if needed
            # For now, we'll just use cache
            
            return Response({
                'message': 'Settings updated successfully',
                'settings': settings_data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoUserPreferencesAPI(APIView):
    """
    Get and update user preferences for todo app
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user preferences"""
        user = request.user
        cache_key = f"todo_preferences_{user.id}"
        
        # Try to get from cache first
        preferences_data = cache.get(cache_key)
        
        if preferences_data is None:
            # Default preferences
            preferences_data = {
                'favorite_filters': [],
                'recent_projects': [],
                'recent_tags': [],
                'dashboard_widgets': [
                    'today_tasks',
                    'overdue_tasks', 
                    'upcoming_deadlines',
                    'progress_overview'
                ],
                'enable_shortcuts': True,
                'custom_shortcuts': {},
                'favorite_templates': [],
                'track_time_spent': True,
                'track_productivity_metrics': True,
                'show_productivity_insights': True,
            }
            
            # Cache for 30 minutes
            cache.set(cache_key, preferences_data, 1800)
        
        serializer = TodoUserPreferencesSerializer(data=preferences_data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(preferences_data)
    
    def post(self, request):
        """Update user preferences"""
        user = request.user
        serializer = TodoUserPreferencesSerializer(data=request.data)
        
        if serializer.is_valid():
            preferences_data = serializer.validated_data
            
            # Save to cache
            cache_key = f"todo_preferences_{user.id}"
            cache.set(cache_key, preferences_data, 1800)
            
            return Response({
                'message': 'Preferences updated successfully',
                'preferences': preferences_data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoDashboardAPI(APIView):
    """
    Get dashboard data for todo app
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get dashboard statistics and data"""
        user = request.user
        
        from ..models import Project, Task, Note
        from django.utils import timezone
        from datetime import timedelta
        
        # Get current date info
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Basic stats
        total_projects = Project.objects.filter(user=user).count()
        active_projects = Project.objects.filter(user=user, status='active').count()
        total_tasks = Task.objects.filter(user=user).count()
        completed_tasks = Task.objects.filter(user=user, status='completed').count()
        
        # Today's tasks
        today_tasks = Task.objects.filter(
            user=user,
            due_date__date=today,
            status__in=['todo', 'in_progress']
        ).count()
        
        # Overdue tasks
        overdue_tasks = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()
        
        # This week's tasks
        week_tasks = Task.objects.filter(
            user=user,
            due_date__date__range=[week_start, week_end],
            status__in=['todo', 'in_progress']
        ).count()
        
        # Notes count
        total_notes = Note.objects.filter(user=user).count()
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_tasks = Task.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count()
        
        completed_this_week = Task.objects.filter(
            user=user,
            completed_at__gte=week_ago,
            status='completed'
        ).count()
        
        dashboard_data = {
            'stats': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'today_tasks': today_tasks,
                'overdue_tasks': overdue_tasks,
                'week_tasks': week_tasks,
                'total_notes': total_notes,
            },
            'activity': {
                'tasks_created_this_week': recent_tasks,
                'tasks_completed_this_week': completed_this_week,
            },
            'quick_access': {
                'recent_projects': Project.objects.filter(user=user).order_by('-updated_at')[:5].values('id', 'name'),
                'important_tasks': Task.objects.filter(user=user, is_important=True, status__in=['todo', 'in_progress'])[:5].values('id', 'title', 'due_date'),
            }
        }
        
        return Response(dashboard_data)