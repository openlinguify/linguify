# backend/apps/progress/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Sum, Q, F
from django.utils.timezone import now
from django.contrib import messages
import datetime
import json
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from .models.progress_course import (
    UserCourseProgress,
    UserLessonProgress,
    UserUnitProgress,
    UserContentLessonProgress
)
from apps.authentication.models import User
from apps.course.models import ContentLesson, Lesson, Unit


class ProgressAdminMixin:
    """Mixin pour les fonctionnalités communes aux admins Progress"""
    actions = ['reset_progress', 'export_progress_data']
    change_list_template = 'admin/progress/change_list_with_stats.html'

    def get_urls(self):
        """Ajoute des URLs personnalisées pour le tableau de bord de progression"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.progress_dashboard_view), name='progress_dashboard'),
            path('api/chart-data/', self.admin_site.admin_view(self.get_chart_data), name='progress_chart_data'),
            path('api/stats/', self.admin_site.admin_view(self.get_stats_data), name='progress_stats_data'),
        ]
        return custom_urls + urls

    def progress_dashboard_view(self, request):
        """Vue pour le tableau de bord de progression"""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Progress Dashboard',
            'has_permission': True,
            'model_name': self.model._meta.model_name,
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
        }
        return render(request, 'admin/progress/dashboard.html', context)

    def get_chart_data(self, request):
        """Fournit les données pour les graphiques du tableau de bord"""
        model = self.model

        # Statistiques par statut
        status_counts = model.objects.values('status').annotate(count=Count('id'))
        status_data = {
            'labels': [s['status'].replace('_', ' ').title() for s in status_counts],
            'data': [s['count'] for s in status_counts],
            'colors': ['#dc3545', '#fd7e14', '#198754']
        }

        # Statistiques par langue
        lang_counts = model.objects.values('language_code').annotate(count=Count('id'))
        lang_counts = sorted(lang_counts, key=lambda x: x['count'], reverse=True)
        lang_data = {
            'labels': [l['language_code'] for l in lang_counts],
            'data': [l['count'] for l in lang_counts]
        }

        # Progression moyenne par jour (30 derniers jours)
        today = now().date()
        thirty_days_ago = today - datetime.timedelta(days=30)
        daily_progress = model.objects.filter(
            last_accessed__date__gte=thirty_days_ago
        ).values(
            'last_accessed__date'
        ).annotate(
            avg_progress=Avg('completion_percentage'),
            count=Count('id')
        ).order_by('last_accessed__date')

        daily_data = {
            'labels': [p['last_accessed__date'].strftime('%Y-%m-%d') for p in daily_progress],
            'avg_progress': [p['avg_progress'] for p in daily_progress],
            'count': [p['count'] for p in daily_progress]
        }

        return JsonResponse({
            'status_data': status_data,
            'language_data': lang_data,
            'daily_data': daily_data
        })

    def get_stats_data(self, request):
        """Fournit les statistiques générales pour le tableau de bord"""
        model = self.model

        total_records = model.objects.count()
        complete_records = model.objects.filter(status='completed').count()
        total_time_spent = model.objects.aggregate(total=Sum('time_spent'))['total'] or 0

        # Convertir le temps total en un format lisible
        minutes, seconds = divmod(total_time_spent, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            total_time_display = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            total_time_display = f"{hours}h {minutes}m"
        else:
            total_time_display = f"{minutes}m {seconds}s"

        # Statistiques supplémentaires spécifiques au modèle
        model_name = self.model._meta.model_name
        special_stats = {}

        if model_name == 'usercontentlessonprogress':
            # Ajouter des statistiques spécifiques aux contenus
            content_type_stats = model.objects.values(
                'content_lesson__content_type'
            ).annotate(
                count=Count('id'),
                complete=Count('id', filter=Q(status='completed')),
                percent_complete=Avg('completion_percentage')
            ).order_by('-count')

            special_stats['content_types'] = [
                {
                    'type': ct['content_lesson__content_type'],
                    'count': ct['count'],
                    'complete': ct['complete'],
                    'percent': round(ct['percent_complete'], 1)
                }
                for ct in content_type_stats
            ]

        return JsonResponse({
            'total_records': total_records,
            'complete_records': complete_records,
            'completion_rate': round(complete_records / total_records * 100, 1) if total_records > 0 else 0,
            'total_time_spent': total_time_spent,
            'total_time_display': total_time_display,
            'special_stats': special_stats
        })

    def reset_progress(self, request, queryset):
        """Action pour réinitialiser la progression des éléments sélectionnés"""
        # Sauvegarde du nombre d'éléments
        count = queryset.count()

        # Réinitialiser les progressions
        queryset.update(
            status='not_started',
            completion_percentage=0,
            score=0,
            completed_at=None,
            time_spent=0
        )

        self.message_user(
            request,
            f'Successfully reset progress for {count} items.',
            messages.SUCCESS
        )
    reset_progress.short_description = "Reset progress for selected items"

    def export_progress_data(self, request, queryset):
        """Action pour exporter les données de progression au format JSON"""
        # Obtenir le nom du modèle pour le nom de fichier
        model_name = self.model._meta.model_name

        # Fonction récursive pour rendre les dates sérialisables
        def json_serial(obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            raise TypeError (f"Type {type(obj)} not serializable")

        # Transformer le queryset en liste de dictionnaires
        data = []
        for item in queryset:
            item_dict = {
                'id': item.id,
                'user': {
                    'id': item.user.id,
                    'username': item.user.username,
                    'email': item.user.email
                },
                'status': item.status,
                'completion_percentage': item.completion_percentage,
                'score': item.score,
                'time_spent': item.time_spent,
                'language_code': item.language_code,
                'last_accessed': item.last_accessed,
                'started_at': item.started_at,
                'completed_at': item.completed_at
            }

            # Ajouter les champs spécifiques selon le modèle
            if model_name == 'userlessonprogress':
                item_dict['lesson'] = {
                    'id': item.lesson.id,
                    'title': item.lesson.title_en,
                    'unit': {
                        'id': item.lesson.unit.id,
                        'title': item.lesson.unit.title_en,
                        'level': item.lesson.unit.level
                    }
                }
            elif model_name == 'usercontentlessonprogress':
                item_dict['content_lesson'] = {
                    'id': item.content_lesson.id,
                    'title': item.content_lesson.title_en if hasattr(item.content_lesson, 'title_en') else str(item.content_lesson),
                    'content_type': item.content_lesson.content_type,
                    'lesson_id': item.content_lesson.lesson_id
                }

            data.append(item_dict)

        # Renvoyer la réponse en format JSON
        response = JsonResponse(
            json.dumps(data, default=json_serial),
            safe=False,
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{model_name}_export.json"'

        return response
    export_progress_data.short_description = "Export selected items to JSON"

    def status_display(self, obj):
        """Affichage du statut avec couleur"""
        colors = {
            'not_started': '#dc3545',
            'in_progress': '#fd7e14',
            'completed': '#198754'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 6px; border-radius: 4px;">{}</span>',
            color,
            obj.status.replace('_', ' ').title()
        )
    status_display.short_description = 'Status'

    def time_display(self, obj):
        """Affichage formaté du temps passé"""
        minutes, seconds = divmod(obj.time_spent, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    time_display.short_description = 'Time Spent'


# Filtres avancés pour l'administration
class CompletionPercentageFilter(admin.SimpleListFilter):
    title = 'Completion Percentage'
    parameter_name = 'completion_percentage'

    def lookups(self, request, model_admin):
        return [
            ('0-25', '0-25%'),
            ('25-50', '25-50%'),
            ('50-75', '50-75%'),
            ('75-99', '75-99%'),
            ('100', 'Completed (100%)')
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-25':
            return queryset.filter(completion_percentage__lte=25)
        elif value == '25-50':
            return queryset.filter(completion_percentage__gt=25, completion_percentage__lte=50)
        elif value == '50-75':
            return queryset.filter(completion_percentage__gt=50, completion_percentage__lte=75)
        elif value == '75-99':
            return queryset.filter(completion_percentage__gt=75, completion_percentage__lt=100)
        elif value == '100':
            return queryset.filter(completion_percentage=100)
        return queryset

class DateRangeFilter(admin.SimpleListFilter):
    title = 'Last Access Date'
    parameter_name = 'last_accessed'

    def lookups(self, request, model_admin):
        return [
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        today = now().date()

        if value == 'today':
            return queryset.filter(last_accessed__date=today)
        elif value == 'yesterday':
            yesterday = today - datetime.timedelta(days=1)
            return queryset.filter(last_accessed__date=yesterday)
        elif value == 'this_week':
            start_of_week = today - datetime.timedelta(days=today.weekday())
            return queryset.filter(last_accessed__date__gte=start_of_week)
        elif value == 'last_week':
            start_of_this_week = today - datetime.timedelta(days=today.weekday())
            start_of_last_week = start_of_this_week - datetime.timedelta(days=7)
            end_of_last_week = start_of_this_week - datetime.timedelta(days=1)
            return queryset.filter(last_accessed__date__gte=start_of_last_week, last_accessed__date__lte=end_of_last_week)
        elif value == 'this_month':
            return queryset.filter(last_accessed__year=today.year, last_accessed__month=today.month)
        elif value == 'last_month':
            if today.month == 1:
                return queryset.filter(last_accessed__year=today.year-1, last_accessed__month=12)
            else:
                return queryset.filter(last_accessed__year=today.year, last_accessed__month=today.month-1)
        elif value == 'this_year':
            return queryset.filter(last_accessed__year=today.year)
        return queryset

class ContentTypeFilter(admin.SimpleListFilter):
    title = 'Content Type'
    parameter_name = 'content_type_name'

    def lookups(self, request, model_admin):
        # Récupérer les différents types de contenu
        content_types = ContentLesson.objects.values_list('content_type', flat=True).distinct()
        return [(ct, ct.replace('_', ' ').title()) for ct in content_types]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(content_lesson__content_type=value)
        return queryset


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(ProgressAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_object_title', 'language_code', 'status_display', 'completion_percentage', 'xp_earned', 'last_accessed')
    list_filter = ('status', 'language_code', 'content_type', CompletionPercentageFilter)
    search_fields = ('user__username', 'user__email', 'language_code')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    list_per_page = 200
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
    
    def content_object_title(self, obj):
        if not obj.content_object:
            return '-'
        
        if hasattr(obj.content_object, 'title_en'):
            return obj.content_object.title_en
        elif hasattr(obj.content_object, 'name'):
            return obj.content_object.name
        else:
            return f"Object #{obj.object_id}"
    content_object_title.short_description = 'Content Title'


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(ProgressAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'lesson_info', 'language_code', 'status_display', 'completion_percentage', 'score', 'time_display', 'last_accessed')
    list_filter = ('status', 'language_code', 'lesson__unit__level', CompletionPercentageFilter, DateRangeFilter)
    search_fields = ('user__username', 'user__email', 'lesson__title_en', 'language_code')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    list_per_page = 200
    date_hierarchy = 'last_accessed'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson', 'lesson__unit')

    def lesson_info(self, obj):
        """Affichage détaillé de la leçon avec lien vers l'admin et niveau"""
        lesson = obj.lesson
        unit = lesson.unit

        # Créer les liens vers l'admin
        lesson_url = reverse('admin:course_lesson_change', args=[lesson.id])
        unit_url = reverse('admin:course_unit_change', args=[unit.id])

        # Badge pour le niveau
        level_badge = f'<span class="badge badge-secondary">{unit.level}</span>'

        # Construction de l'affichage avec liens
        return format_html(
            '<a href="{}">{}</a> in <a href="{}">{}</a> {}',
            lesson_url,
            lesson.title_en,
            unit_url,
            unit.title_en,
            level_badge
        )
    lesson_info.short_description = 'Lesson'
    lesson_info.admin_order_field = 'lesson__title_en'

    def get_actions(self, request):
        """Ajoute une action spécifique pour synchroniser les progressions de contenu"""
        actions = super().get_actions(request)
        actions['sync_content_lessons_progress'] = (
            self.sync_content_lessons_progress,
            'sync_content_lessons_progress',
            'Synchronize with content lesson progress'
        )
        return actions

    def sync_content_lessons_progress(self, request, queryset):
        """Action pour synchroniser les progressions de leçon avec les progressions de contenu"""
        sync_count = 0
        created_count = 0

        for lesson_progress in queryset:
            # Récupérer les contenus de cette leçon
            content_lessons = ContentLesson.objects.filter(lesson=lesson_progress.lesson)

            if not content_lessons.exists():
                continue

            # Pour chaque contenu, vérifier s'il a une progression
            for content_lesson in content_lessons:
                content_progress, created = UserContentLessonProgress.objects.get_or_create(
                    user=lesson_progress.user,
                    content_lesson=content_lesson,
                    language_code=lesson_progress.language_code,
                    defaults={
                        'status': 'not_started',
                        'completion_percentage': 0
                    }
                )

                if created:
                    created_count += 1
                else:
                    sync_count += 1

                    # Si la leçon est terminée mais pas le contenu, mettre à jour
                    if lesson_progress.status == 'completed' and content_progress.status != 'completed':
                        content_progress.status = 'completed'
                        content_progress.completion_percentage = 100

                        # Répartir le temps équitablement entre les contenus
                        content_count = content_lessons.count()
                        content_progress.time_spent = lesson_progress.time_spent // content_count

                        # Marquer comme complété avec la date de la leçon
                        if lesson_progress.completed_at and not content_progress.completed_at:
                            content_progress.completed_at = lesson_progress.completed_at

                        content_progress.save()

        self.message_user(
            request,
            f'Successfully synchronized {sync_count} content progresses and created {created_count} new ones.',
            messages.SUCCESS
        )
    sync_content_lessons_progress.short_description = "Synchronize with content lesson progress"


@admin.register(UserUnitProgress)
class UserUnitProgressAdmin(ProgressAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'unit_info', 'language_code', 'status_display', 'completion_percentage', 'score', 'time_display', 'last_accessed')
    list_filter = ('status', 'language_code', 'unit__level', CompletionPercentageFilter, DateRangeFilter)
    search_fields = ('user__username', 'user__email', 'unit__title_en', 'language_code')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    list_per_page = 200
    date_hierarchy = 'last_accessed'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'unit')

    def unit_info(self, obj):
        """Affichage détaillé de l'unité avec lien vers l'admin"""
        unit = obj.unit
        unit_url = reverse('admin:course_unit_change', args=[unit.id])

        # Badge coloré pour le niveau (différentes couleurs par niveau)
        level_colors = {
            'A1': '#28a745',  # Vert
            'A2': '#17a2b8',  # Teal
            'B1': '#007bff',  # Bleu
            'B2': '#6f42c1',  # Violet
            'C1': '#fd7e14',  # Orange
            'C2': '#dc3545'   # Rouge
        }
        color = level_colors.get(unit.level, '#6c757d')  # Gris par défaut

        level_badge = format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            unit.level
        )

        # Lien vers l'unité avec niveau formaté
        return format_html(
            '<a href="{}">{}</a> {}',
            unit_url,
            unit.title_en,
            level_badge
        )
    unit_info.short_description = 'Unit'
    unit_info.admin_order_field = 'unit__title_en'

    def get_actions(self, request):
        """Ajoute une action spécifique pour synchroniser les progressions de leçon"""
        actions = super().get_actions(request)
        actions['recalculate_from_lessons'] = (
            self.recalculate_from_lessons,
            'recalculate_from_lessons',
            'Recalculate from lesson progress'
        )
        return actions

    def recalculate_from_lessons(self, request, queryset):
        """Action pour recalculer la progression des unités basée sur les progressions de leçon"""
        updated_count = 0

        for unit_progress in queryset:
            # Récupérer les leçons de cette unité
            lessons = Lesson.objects.filter(unit=unit_progress.unit)

            if not lessons.exists():
                continue

            # Récupérer les progressions de leçon associées
            lesson_progresses = UserLessonProgress.objects.filter(
                user=unit_progress.user,
                lesson__in=lessons,
                language_code=unit_progress.language_code
            )

            if lesson_progresses.exists():
                # Calcul de la progression moyenne
                avg_percentage = lesson_progresses.aggregate(avg=Avg('completion_percentage'))['avg'] or 0
                completed_count = lesson_progresses.filter(status='completed').count()
                total_count = lessons.count()

                # Mise à jour de la progression de l'unité
                if completed_count == total_count and total_count > 0:
                    unit_progress.status = 'completed'
                    unit_progress.completion_percentage = 100
                    if not unit_progress.completed_at:
                        unit_progress.completed_at = now()
                else:
                    unit_progress.status = 'in_progress' if avg_percentage > 0 else 'not_started'
                    unit_progress.completion_percentage = round(avg_percentage)

                # Mise à jour du temps et du score
                unit_progress.time_spent = lesson_progresses.aggregate(total=Sum('time_spent'))['total'] or 0

                # Mettre à jour le score si des leçons ont des scores
                lessons_with_scores = lesson_progresses.filter(score__gt=0)
                if lessons_with_scores.exists():
                    unit_progress.score = round(lessons_with_scores.aggregate(avg=Avg('score'))['avg'] or 0)

                unit_progress.save()
                updated_count += 1

        self.message_user(
            request,
            f'Successfully recalculated {updated_count} unit progresses from lesson data.',
            messages.SUCCESS
        )
    recalculate_from_lessons.short_description = "Recalculate from lesson progress"


@admin.register(UserContentLessonProgress)
class UserContentLessonProgressAdmin(ProgressAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'content_lesson_info', 'language_code', 'status_display', 'completion_percentage', 'score', 'time_display', 'last_accessed')
    list_filter = ('status', 'language_code', ContentTypeFilter, CompletionPercentageFilter, DateRangeFilter)
    search_fields = ('user__username', 'user__email', 'content_lesson__title_en', 'language_code')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    list_per_page = 200
    date_hierarchy = 'last_accessed'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_lesson', 'content_lesson__lesson', 'content_lesson__lesson__unit')

    def content_lesson_info(self, obj):
        """Affichage détaillé du contenu de leçon avec lien vers l'admin"""
        content_lesson = obj.content_lesson
        lesson_title = content_lesson.title_en if hasattr(content_lesson, 'title_en') else "Unknown"
        content_type = content_lesson.content_type
        parent_lesson = content_lesson.lesson.title_en if content_lesson.lesson else "No parent"

        # Créer les liens vers l'admin du contenu et de la leçon parente
        content_url = reverse('admin:course_contentlesson_change', args=[content_lesson.id])
        lesson_url = ''
        if content_lesson.lesson:
            lesson_url = reverse('admin:course_lesson_change', args=[content_lesson.lesson.id])
            lesson_link = f'<a href="{lesson_url}">{parent_lesson}</a>'
        else:
            lesson_link = parent_lesson

        # Icône qui représente le type de contenu
        icons = {
            'vocabulary': '📚',
            'multiple_choice': '❓',
            'matching': '🔄',
            'speaking': '🗣️',
            'theory': '📘',
            'fill_blank': '✏️'
        }
        icon = icons.get(content_type, '📝')

        # Construction de l'affichage avec icône et liens
        return format_html(
            '{} <a href="{}">{}</a> <span class="badge badge-info">{}</span> - Lesson: {}',
            icon,
            content_url,
            lesson_title,
            content_type.replace('_', ' ').title(),
            lesson_link
        )
    content_lesson_info.short_description = 'Content Lesson'
    content_lesson_info.admin_order_field = 'content_lesson__title_en'

    def get_actions(self, request):
        """Ajoute une action spécifique pour réanalyser les progrès de contenu"""
        actions = super().get_actions(request)
        actions['recalculate_parent_lesson_progress'] = (
            self.recalculate_parent_lesson_progress,
            'recalculate_parent_lesson_progress',
            'Recalculate parent lesson progress'
        )
        return actions

    def recalculate_parent_lesson_progress(self, request, queryset):
        """Action pour recalculer la progression des leçons parentes"""
        updated_lessons = set()

        for progress in queryset:
            if progress.content_lesson and progress.content_lesson.lesson:
                parent_lesson = progress.content_lesson.lesson
                updated_lessons.add(parent_lesson.id)

        # Récupérer les progressions de leçon correspondantes et mettre à jour
        lesson_progresses = UserLessonProgress.objects.filter(
            lesson_id__in=updated_lessons,
            user__in=queryset.values_list('user', flat=True),
            language_code__in=queryset.values_list('language_code', flat=True)
        )

        # Pour chaque leçon, mettre à jour la progression basée sur ses contenus
        for lesson_progress in lesson_progresses:
            content_progresses = UserContentLessonProgress.objects.filter(
                content_lesson__lesson=lesson_progress.lesson,
                user=lesson_progress.user,
                language_code=lesson_progress.language_code
            )

            if content_progresses.exists():
                # Calcul de la progression moyenne
                avg_percentage = content_progresses.aggregate(avg=Avg('completion_percentage'))['avg'] or 0
                completed_count = content_progresses.filter(status='completed').count()
                total_count = content_progresses.count()

                # Mise à jour de la progression de la leçon
                if completed_count == total_count:
                    lesson_progress.status = 'completed'
                    lesson_progress.completion_percentage = 100
                    if not lesson_progress.completed_at:
                        lesson_progress.completed_at = now()
                else:
                    lesson_progress.status = 'in_progress' if avg_percentage > 0 else 'not_started'
                    lesson_progress.completion_percentage = round(avg_percentage)

                # Mise à jour des temps et scores
                lesson_progress.time_spent = content_progresses.aggregate(total=Sum('time_spent'))['total'] or 0
                lesson_progress.save()

        self.message_user(
            request,
            f'Successfully recalculated progress for {len(updated_lessons)} parent lessons.',
            messages.SUCCESS
        )
    recalculate_parent_lesson_progress.short_description = "Recalculate parent lesson progress for selected items"