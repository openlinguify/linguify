from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
import json
from .models import *


class UserLearningProfileInline(admin.StackedInline):
    """Inline for UserLearningProfile to be used in User admin"""
    model = UserLearningProfile
    can_delete = False
    verbose_name_plural = "Language Learning Profile"
    fk_name = "user"
    fieldsets = (
        ('Learning Languages', {
            'fields': ('native_language', 'target_language', 'language_level', 'objectives')
        }),
        ('Exercise Preferences', {
            'fields': ('speaking_exercises', 'listening_exercises', 'reading_exercises', 'writing_exercises'),
            'classes': ('collapse',),
        }),
        ('Study Goals & Reminders', {
            'fields': ('daily_goal', 'weekday_reminders', 'weekend_reminders', 'reminder_time'),
            'classes': ('collapse',),
        }),
    )
    extra = 0


@admin.register(LanguagelearningItem)
class LanguagelearningItemAdmin(admin.ModelAdmin):
    """Administration des items Language Learning"""
    
    list_display = ['title', 'user', 'item_type', 'difficulty', 'language', 'is_active', 'created_at']
    list_filter = ['is_active', 'item_type', 'difficulty', 'language', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'item_type', 'difficulty', 'language', 'is_active')
        }),
        ('Détails', {
            'fields': ('content', 'estimated_duration', 'order_index'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'language')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Administration des langues"""
    
    list_display = ['name', 'code', 'native_name', 'flag_emoji', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'native_name', 'code']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'native_name', 'flag_emoji', 'is_active')
        }),
    )


@admin.register(UserLanguage)
class UserLanguageAdmin(admin.ModelAdmin):
    """Administration des langues utilisateur"""
    
    list_display = ['user', 'language', 'language_level', 'target_level', 'progress_percentage', 'is_active']
    list_filter = ['language_level', 'target_level', 'is_active', 'started_at']
    search_fields = ['user__username', 'language__name']
    readonly_fields = ['started_at', 'last_activity']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'language', 'language_level', 'target_level', 'is_active')
        }),
        ('Objectifs', {
            'fields': ('daily_goal', 'progress_percentage')
        }),
        ('Statistiques', {
            'fields': ('streak_count', 'total_time_spent', 'lessons_completed'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('started_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'language')


@admin.register(UserLearningProfile)
class UserLearningProfileAdmin(admin.ModelAdmin):
    """Administration des profils d'apprentissage"""

    list_display = ['user', 'native_language', 'target_language', 'language_level', 'objectives', 'daily_goal', 'updated_at']
    list_filter = ['native_language', 'target_language', 'language_level', 'objectives', 'speaking_exercises', 'listening_exercises']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Langues et Objectifs', {
            'fields': ('native_language', 'target_language', 'language_level', 'objectives')
        }),
        ('Préférences d\'Exercices', {
            'fields': ('speaking_exercises', 'listening_exercises', 'reading_exercises', 'writing_exercises'),
            'classes': ('collapse',)
        }),
        ('Objectifs et Rappels', {
            'fields': ('daily_goal', 'weekday_reminders', 'weekend_reminders', 'reminder_time'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('streak_count', 'total_time_spent', 'lessons_completed', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Administration des leçons"""
    
    list_display = ['title', 'language', 'level', 'order', 'estimated_duration', 'is_published']
    list_filter = ['language', 'level', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['language', 'level', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('language', 'title', 'description', 'level', 'order', 'is_published')
        }),
        ('Contenu', {
            'fields': ('content', 'estimated_duration'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('language')


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    """Administration du progrès des leçons"""
    
    list_display = ['user', 'lesson', 'is_completed', 'score', 'time_spent', 'attempts', 'updated_at']
    list_filter = ['is_completed', 'lesson__language', 'completed_at', 'updated_at']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'lesson', 'is_completed', 'score', 'attempts')
        }),
        ('Statistiques', {
            'fields': ('time_spent', 'completed_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson', 'lesson__language')


@admin.register(LanguageLearningSettings)
class LanguageLearningSettingsAdmin(admin.ModelAdmin):
    """Administration des paramètres d'apprentissage des langues"""
    
    list_display = ['user', 'daily_goal_minutes', 'preferred_difficulty', 'reminder_enabled', 'updated_at']
    list_filter = ['preferred_difficulty', 'reminder_enabled', 'auto_difficulty_adjustment', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Objectifs', {
            'fields': ('daily_goal_minutes', 'weekly_goal_days', 'preferred_study_time')
        }),
        ('Notifications', {
            'fields': ('reminder_enabled', 'reminder_frequency', 'streak_notifications', 'achievement_notifications'),
            'classes': ('collapse',)
        }),
        ('Difficulté', {
            'fields': ('preferred_difficulty', 'auto_difficulty_adjustment'),
            'classes': ('collapse',)
        }),
        ('Interface', {
            'fields': ('show_pronunciation_hints', 'enable_audio_playback', 'audio_playback_speed', 'show_progress_animations', 'font_size'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# =============================================================================
# ADMINISTRATION DES COURS ET MODULES
# =============================================================================

class ExerciseContentWidget(forms.Textarea):
    """Widget personnalisé pour éditer le contenu des exercices en JSON"""

    class Media:
        css = {
            'all': ('admin/css/exercise_editor.css',)
        }
        js = ('admin/js/exercise_editor.js',)

    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 20,
            'cols': 80,
            'style': 'font-family: monospace; font-size: 14px;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class CourseModuleForm(forms.ModelForm):
    """Formulaire personnalisé pour l'édition des modules"""

    content = forms.JSONField(
        widget=ExerciseContentWidget,
        help_text="""
        Format JSON pour les exercices:
        {
            "exercises": [
                {
                    "type": "multiple_choice",
                    "question": "Votre question",
                    "prompt": "Instructions",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Explication de la réponse"
                },
                {
                    "type": "translation",
                    "text_to_translate": "Texte à traduire",
                    "correct_answer": ["Réponse 1", "Réponse 2"],
                    "explanation": "Explication"
                },
                {
                    "type": "fill_blank",
                    "question": "Question",
                    "sentence_with_blank": "Phrase avec _____",
                    "placeholder": "Indice",
                    "correct_answer": ["Réponse"],
                    "explanation": "Explication"
                },
                {
                    "type": "audio",
                    "audio_url": "/static/audio/file.mp3",
                    "correct_answer": ["Réponse"],
                    "explanation": "Explication"
                }
            ]
        }
        """,
        required=False
    )

    class Meta:
        model = CourseModule
        fields = '__all__'

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            try:
                if isinstance(content, str):
                    content = json.loads(content)

                # Valider la structure des exercices
                if 'exercises' in content:
                    for i, exercise in enumerate(content['exercises']):
                        if 'type' not in exercise:
                            raise forms.ValidationError(f"Exercice {i+1}: Le champ 'type' est requis")

                        if exercise['type'] not in ['multiple_choice', 'translation', 'fill_blank', 'audio']:
                            raise forms.ValidationError(f"Exercice {i+1}: Type invalide '{exercise['type']}'")

                return content
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f"JSON invalide: {e}")

        return content or {}


class CourseModuleInline(admin.TabularInline):
    """Inline pour les modules d'une unité"""
    model = CourseModule
    extra = 1
    fields = ['module_number', 'title', 'module_type', 'estimated_duration', 'xp_reward', 'is_locked', 'order']
    ordering = ['order', 'module_number']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'module_number')


@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):
    """Administration des unités de cours"""

    list_display = ['title', 'language', 'unit_number', 'modules_count_display', 'order', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['language', 'order', 'unit_number']
    inlines = [CourseModuleInline]

    fieldsets = (
        (None, {
            'fields': ('language', 'unit_number', 'title', 'description', 'is_active')
        }),
        ('Apparence', {
            'fields': ('icon', 'color', 'order'),
            'classes': ('collapse',)
        }),
    )

    def modules_count_display(self, obj):
        count = obj.modules.count()
        return format_html(
            '<span style="color: {};">{} modules</span>',
            '#28a745' if count > 0 else '#dc3545',
            count
        )
    modules_count_display.short_description = 'Modules'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('language').prefetch_related('modules')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Administration des modules de cours"""

    form = CourseModuleForm
    list_display = ['title', 'unit', 'module_type', 'estimated_duration', 'xp_reward', 'exercises_count_display', 'is_locked']
    list_filter = ['module_type', 'unit__language', 'is_locked']
    search_fields = ['title', 'description', 'unit__title']
    ordering = ['unit', 'order', 'module_number']
    actions = ['create_sample_exercises']

    fieldsets = (
        (None, {
            'fields': ('unit', 'module_number', 'title', 'module_type', 'description')
        }),
        ('Configuration', {
            'fields': ('estimated_duration', 'xp_reward', 'is_locked', 'order')
        }),
        ('Contenu et Exercices', {
            'fields': ('content',),
            'description': 'Définissez ici les exercices du module au format JSON'
        }),
    )

    def exercises_count_display(self, obj):
        content = obj.content or {}
        exercises = content.get('exercises', [])
        count = len(exercises)

        if count == 0:
            return format_html('<span style="color: #dc3545;">Aucun exercice</span>')
        else:
            return format_html(
                '<span style="color: #28a745;">{} exercice{}</span>',
                count,
                's' if count > 1 else ''
            )
    exercises_count_display.short_description = 'Exercices'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('unit', 'unit__language')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Pré-remplir le contenu avec un exemple si vide
        if obj and not obj.content:
            if obj.module_type == 'vocabulary':
                example_content = {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": "Comment dit-on 'Bonjour' en espagnol ?",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                            "correct_answer": "Hola",
                            "explanation": "Hola est la salutation la plus courante en espagnol."
                        }
                    ]
                }
            elif obj.module_type == 'grammar':
                example_content = {
                    "exercises": [
                        {
                            "type": "fill_blank",
                            "question": "Complétez avec l'article correct",
                            "sentence_with_blank": "_____ casa es muy grande.",
                            "placeholder": "article",
                            "correct_answer": ["La"],
                            "explanation": "'Casa' est féminin, donc on utilise 'la'."
                        }
                    ]
                }
            else:
                example_content = {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": f"Question d'exemple pour {obj.get_module_type_display()}",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "Explication de la réponse correcte."
                        }
                    ]
                }

            form.base_fields['content'].initial = json.dumps(example_content, indent=2, ensure_ascii=False)

        return form

    @admin.action(description='Créer des exercices d\'exemple pour les modules sélectionnés')
    def create_sample_exercises(self, request, queryset):
        """Action pour créer des exercices d'exemple"""
        updated = 0
        for module in queryset:
            if not module.content or not module.content.get('exercises'):
                if module.module_type == 'vocabulary':
                    sample_exercises = [
                        {
                            "type": "multiple_choice",
                            "question": f"Question de vocabulaire pour {module.title}",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "Explication de la réponse."
                        },
                        {
                            "type": "translation",
                            "text_to_translate": "Texte à traduire",
                            "correct_answer": ["Traduction"],
                            "explanation": "Explication de la traduction."
                        }
                    ]
                elif module.module_type == 'grammar':
                    sample_exercises = [
                        {
                            "type": "fill_blank",
                            "question": f"Exercice de grammaire pour {module.title}",
                            "sentence_with_blank": "Phrase avec _____ à compléter.",
                            "placeholder": "mot manquant",
                            "correct_answer": ["réponse"],
                            "explanation": "Explication grammaticale."
                        }
                    ]
                else:
                    sample_exercises = [
                        {
                            "type": "multiple_choice",
                            "question": f"Question pour {module.title}",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "Explication de la réponse."
                        }
                    ]

                module.content = {"exercises": sample_exercises}
                module.save()
                updated += 1

        self.message_user(request, f"{updated} modules mis à jour avec des exercices d'exemple.")


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    """Administration de la progression des modules"""

    list_display = ['user', 'module_title', 'module_type', 'is_completed', 'score', 'attempts', 'last_accessed']
    list_filter = ['is_completed', 'module__module_type', 'module__unit__language', 'completion_date']
    search_fields = ['user__username', 'module__title', 'module__unit__title']
    readonly_fields = ['last_accessed']
    date_hierarchy = 'last_accessed'

    fieldsets = (
        (None, {
            'fields': ('user', 'module', 'is_completed', 'score', 'attempts')
        }),
        ('Temps', {
            'fields': ('time_spent', 'completion_date', 'last_accessed')
        }),
    )

    def module_title(self, obj):
        return obj.module.title
    module_title.short_description = 'Module'

    def module_type(self, obj):
        return obj.module.get_module_type_display()
    module_type.short_description = 'Type'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'module', 'module__unit')


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    """Administration de la progression globale des utilisateurs"""

    list_display = ['user', 'language', 'level', 'total_xp', 'completion_percentage', 'last_activity_date']
    list_filter = ['language', 'level', 'started_date']
    search_fields = ['user__username', 'language__name']
    readonly_fields = ['started_date', 'last_activity_date']
    date_hierarchy = 'last_activity_date'

    fieldsets = (
        (None, {
            'fields': ('user', 'language', 'current_unit', 'current_module')
        }),
        ('Progression', {
            'fields': ('total_xp', 'level')
        }),
        ('Dates', {
            'fields': ('started_date', 'last_activity_date')
        }),
    )

    def completion_percentage(self, obj):
        percentage = obj.get_completion_percentage()
        color = '#28a745' if percentage >= 75 else '#ffc107' if percentage >= 25 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            f"{percentage}%"
        )
    completion_percentage.short_description = 'Completion'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'language', 'current_unit', 'current_module')
