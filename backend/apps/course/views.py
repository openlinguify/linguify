from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from .models.core import Unit
from .models.progress import UserProgress, UnitProgress, LessonProgress
import json
import logging

logger = logging.getLogger(__name__)


class CourseDashboardView(TemplateView):
    """Vue principale du tableau de bord d'apprentissage"""
    template_name = 'course/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Utiliser l'admin user pour les données
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = self.request.user
        
        return self._get_dashboard_context(admin_user, context)
        
    def _get_dashboard_context(self, user, context=None):
        """Méthode helper pour obtenir le contexte du dashboard"""
        if context is None:
            context = {}
            
        # Statistiques utilisateur
        user_stats = self.get_user_stats(user)
        
        # Cours marketplace
        marketplace_courses = self.get_marketplace_courses()
        marketplace_stats = self.get_marketplace_stats()
        
        # Cours de l'utilisateur
        my_courses = self.get_my_courses(user)
        
        # Cours à continuer
        continue_learning = self.get_continue_learning(user)
        
        # Ajouter au contexte
        context.update({
            'user_stats': user_stats,
            'marketplace_courses': marketplace_courses,
            'marketplace_stats': marketplace_stats,
            'my_courses': my_courses,
            'continue_learning': continue_learning,
        })
        
        # Convertir en JSON pour JavaScript
        context.update({
            'user_stats_json': json.dumps(user_stats),
            'marketplace_courses_json': json.dumps(marketplace_courses),
            'marketplace_stats_json': json.dumps(marketplace_stats),
            'my_courses_json': json.dumps(my_courses),
            'continue_learning_json': json.dumps(continue_learning),
        })
        
        return context
    
    def get_user_stats(self, user):
        """Statistiques de progression de l'utilisateur"""
        # Obtenir ou créer la progression globale de l'utilisateur
        user_progress, created = UserProgress.objects.get_or_create(user=user)
        
        # Compter les leçons terminées
        completed_lessons = LessonProgress.objects.filter(
            user=user, 
            status='completed'
        ).count()
        
        # Compter le total de leçons commencées
        total_lessons = LessonProgress.objects.filter(user=user).count()
        
        return {
            'overall_progress': user_progress.overall_progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'streak_days': user_progress.streak_days,
            'total_xp': user_progress.total_xp,
            'level': user_progress.current_level,
            'study_time_today': 0,  # À implémenter
        }
    
    def get_marketplace_courses(self):
        """Cours disponibles sur le marketplace groupés par niveau"""
        units = Unit.objects.filter(is_published=True, teacher_id__isnull=False)
        
        # Grouper par niveau
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        level_names = {
            'A1': 'Débutant',
            'A2': 'Élémentaire', 
            'B1': 'Intermédiaire',
            'B2': 'Intermédiaire+',
            'C1': 'Avancé',
            'C2': 'Maîtrise'
        }
        
        marketplace_courses = []
        
        for level in levels:
            units_for_level = units.filter(level=level)
            if units_for_level.exists():
                courses = []
                for unit in units_for_level:
                    # Vérifier si l'utilisateur est inscrit
                    user = getattr(self.request, 'user', None)
                    is_enrolled = False
                    if user and user.is_authenticated:
                        is_enrolled = UnitProgress.objects.filter(
                            user=user, unit=unit
                        ).exists()
                    
                    course = {
                        'id': unit.id,
                        'title': unit.title,
                        'instructor': unit.teacher_name or 'Équipe Linguify',
                        'description': unit.description,
                        'level': level,
                        'price': float(unit.price),
                        'is_free': unit.is_free,
                        'is_enrolled': is_enrolled,
                        'rating': 4.5,  # Données factices pour l'instant
                        'reviews_count': 25,
                        'students_count': 150,
                    }
                    courses.append(course)
                
                marketplace_courses.append({
                    'level': level,
                    'level_name': level_names[level],
                    'courses': courses
                })
        
        return marketplace_courses
    
    def get_marketplace_stats(self):
        """Statistiques du marketplace"""
        total_courses = Unit.objects.filter(is_published=True).count()
        free_courses = Unit.objects.filter(is_published=True, is_free=True).count()
        
        return {
            'total_courses': total_courses,
            'free_courses': free_courses,
            'instructors': 2,  # À calculer dynamiquement
            'levels': 6,
        }
    
    def get_my_courses(self, user):
        """Cours auxquels l'utilisateur est inscrit"""
        unit_progress = UnitProgress.objects.filter(user=user).select_related('unit')
        
        my_courses = []
        for progress in unit_progress:
            unit = progress.unit
            course = {
                'id': unit.id,
                'title': unit.title,
                'instructor': unit.teacher_name or 'Équipe Linguify',
                'level': unit.level,
                'progress': progress.progress_percentage,
                'status': 'completed' if progress.is_completed else 'in-progress',
                'completed_lessons': progress.lessons_completed,
                'total_lessons': progress.total_lessons,
            }
            my_courses.append(course)
        
        return my_courses
    
    def get_continue_learning(self, user):
        """Leçons à continuer"""
        # Trouver les cours en cours avec la prochaine leçon
        continue_items = []
        
        in_progress = UnitProgress.objects.filter(
            user=user, 
            status__in=['not_started', 'in_progress']
        ).select_related('unit')
        
        for progress in in_progress:
            # Obtenir la prochaine leçon
            next_lesson = progress.get_next_lesson()
            
            if next_lesson:
                item = {
                    'lesson_id': next_lesson.id,
                    'course_title': progress.unit.title,
                    'lesson_title': next_lesson.title,
                    'progress': progress.progress_percentage,
                }
                continue_items.append(item)
        
        return continue_items


@login_required
def learning_redirect(request):
    """Redirection vers le dashboard d'apprentissage"""
    return render(request, 'course/dashboard.html')


def test_marketplace_view(request):
    """Vue de test pour voir les données du marketplace sans authentification"""
    from django.http import JsonResponse
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        return JsonResponse({'error': 'Admin user not found'})
    
    # Utiliser la même logique que CourseDashboardView
    view = CourseDashboardView()
    
    # Mock request
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    view.request = MockRequest(admin_user)
    
    # Obtenir les données
    marketplace_courses = view.get_marketplace_courses()
    marketplace_stats = view.get_marketplace_stats()
    my_courses = view.get_my_courses(admin_user)
    continue_learning = view.get_continue_learning(admin_user)
    
    return JsonResponse({
        'success': True,
        'data': {
            'marketplace_courses': marketplace_courses,
            'marketplace_stats': marketplace_stats,
            'my_courses': my_courses,
            'continue_learning': continue_learning,
            'message': 'Données récupérées avec succès! Connectez-vous pour voir l\'interface complète.'
        }
    }, json_dumps_params={'indent': 2})



def demo_dashboard_view(request):
    """Vue de démonstration qui affiche le dashboard avec des données sans authentification"""
    from django.contrib.auth import get_user_model
    import json
    
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = None
    
    if admin_user:
        # Utiliser la même logique que CourseDashboardView
        view = CourseDashboardView()
        
        # Mock request
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        view.request = MockRequest(admin_user)
        
        # Obtenir les données
        user_stats = view.get_user_stats(admin_user)
        marketplace_courses = view.get_marketplace_courses()
        marketplace_stats = view.get_marketplace_stats()
        my_courses = view.get_my_courses(admin_user)
        continue_learning = view.get_continue_learning(admin_user)
        
        context = {
            'user': admin_user,
            'user_stats': user_stats,
            'marketplace_courses': marketplace_courses,
            'marketplace_stats': marketplace_stats,
            'my_courses': my_courses,
            'continue_learning': continue_learning,
            'user_stats_json': json.dumps(user_stats),
            'marketplace_courses_json': json.dumps(marketplace_courses),
            'marketplace_stats_json': json.dumps(marketplace_stats),
            'my_courses_json': json.dumps(my_courses),
            'continue_learning_json': json.dumps(continue_learning),
        }
    else:
        context = {
            'user': None,
            'error': 'Admin user not found'
        }
    
    return render(request, 'course/dashboard_modular.html', context)


@method_decorator(login_required, name='dispatch')
class LearningSettingsView(View):
    """Handle learning settings for the user"""
    
    def post(self, request):
        """Handle learning settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data
            data = {
                'daily_goal': request.POST.get('daily_goal', '30'),
                'reminder_enabled': request.POST.get('reminder_enabled') == 'on',
                'reminder_time': request.POST.get('reminder_time', '19:00'),
                'auto_play_audio': request.POST.get('auto_play_audio') == 'on',
                'show_pronunciation': request.POST.get('show_pronunciation') == 'on',
                'difficulty_level': request.POST.get('difficulty_level', 'adaptive'),
                'lesson_pace': request.POST.get('lesson_pace', 'normal'),
                'practice_mode': request.POST.get('practice_mode', 'mixed'),
            }
            
            # Store in user session for now
            session_key = f'learning_settings_{request.user.id}'
            request.session[session_key] = data
            logger.info(f"Learning settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres d\'apprentissage mis à jour avec succès',
                    'data': data
                })
            else:
                messages.success(request, 'Paramètres d\'apprentissage mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in learning settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres d\'apprentissage'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=500)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display learning settings page"""
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session
            session_key = f'learning_settings_{request.user.id}'
            settings = request.session.get(session_key, {
                'daily_goal': '30',
                'reminder_enabled': True,
                'reminder_time': '19:00',
                'auto_play_audio': True,
                'show_pronunciation': True,
                'difficulty_level': 'adaptive',
                'lesson_pace': 'normal',
                'practice_mode': 'mixed',
            })
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Use centralized settings context
                from app_manager.mixins import SettingsContextMixin
                mixin = SettingsContextMixin()
                context = mixin.get_settings_context(
                    user=request.user,
                    active_tab_id='learning',
                    page_title='Apprentissage',
                    page_subtitle='Configurez vos préférences d\'apprentissage et objectifs'
                )
                
                # Add learning-specific data
                context.update({
                    'title': 'Paramètres d\'Apprentissage - Linguify',
                    'learning_settings': settings,
                })
                
                return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error retrieving learning settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=500)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres d'apprentissage")
                return redirect('saas_web:settings')