# course/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django import forms
from django.urls import path, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
import csv, io, json

from .widgets import AdminJSONFormField
from .admin_filters import PairsStatusFilter, PairsCountRangeFilter
from .models import (
    Unit, 
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    ExerciseVocabularyMultipleChoice, 
    MultipleChoiceQuestion, 
    Numbers,
    MatchingExercise,
    ExerciseGrammarReordering,
    FillBlankExercise,
    SpeakingExercise,
    TestRecap,
    TestRecapQuestion,
    TestRecapResult
)

from django.forms.widgets import CheckboxSelectMultiple

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    show_change_link = True
    fields = ('title_en', 'lesson_type', 'estimated_duration', 'order')
    ordering = ('order',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_title', 'level', 'order', 'lesson_count')
    list_filter = ('level', )
    search_fields = ('title_en', 'title_fr', 'title_es', 'title_nl')
    ordering = ('order', 'id')
    inlines = [LessonInline]
    
    def get_title(self, obj):
        return f"{obj.title_en} | {obj.title_fr}"
    get_title.short_description = 'Title'
    
    def lesson_count(self, obj):
        count = obj.lessons.count()
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if count > 0 else 'red', 
                          f"{count} lessons")
    lesson_count.short_description = 'Lessons'

class ContentLessonInline(admin.TabularInline):
    model = ContentLesson
    extra = 0
    show_change_link = True
    fields = ('title_en', 'content_type', 'order')
    ordering = ('order',)


@admin.register(ContentLesson)
class ContentLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_en', 'content_type', 'lesson', 'order', 'estimated_duration')
    list_filter = ('content_type', 'lesson__unit', 'lesson__lesson_type')
    search_fields = ('title_en', 'title_fr', 'instruction_en')
    ordering = ('lesson', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'content_type', 'order', 'estimated_duration')
        }),
        ('Titles', {
            'fields': ('title_en', 'title_fr', 'title_es', 'title_nl')
        }),
        ('Instructions', {
            'fields': ('instruction_en', 'instruction_fr', 'instruction_es', 'instruction_nl')
        }),
    )


class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        lesson_type = cleaned_data.get('lesson_type')
        professional_field = cleaned_data.get('professional_field')
        
        if lesson_type == 'professional' and not professional_field:
            self.add_error('professional_field', 'Ce champ est obligatoire pour les leçons professionnelles.')
        
        return cleaned_data

# Formulaire de création rapide d'exercice de matching
class QuickMatchingExerciseForm(forms.Form):
    lesson = forms.ModelChoiceField(
        queryset=Lesson.objects.all().order_by('unit__level', 'unit__order', 'order'),
        label="Lesson",
        help_text="Sélectionnez la leçon pour cet exercice"
    )
    
    title_en = forms.CharField(
        max_length=255,
        label="Titre (EN)",
        initial="Matching Exercise"
    )
    
    title_fr = forms.CharField(
        max_length=255,
        label="Titre (FR)",
        initial="Exercice d'association"
    )
    
    title_es = forms.CharField(
        max_length=255,
        label="Titre (ES)",
        initial="Ejercicio de emparejamiento"
    )
    
    title_nl = forms.CharField(
        max_length=255,
        label="Titre (NL)",
        initial="Matching oefening"
    )
    
    instruction_en = forms.CharField(
        max_length=255,
        initial="Match the words with their translations",
        label="Instruction (EN)"
    )
    
    instruction_fr = forms.CharField(
        max_length=255,
        initial="Associez les mots à leurs traductions",
        label="Instruction (FR)"
    )
    
    instruction_es = forms.CharField(
        max_length=255,
        initial="Relaciona las palabras con sus traducciones",
        label="Instruction (ES)"
    )
    
    instruction_nl = forms.CharField(
        max_length=255,
        initial="Koppel de woorden aan hun vertalingen",
        label="Instruction (NL)"
    )
    
    estimated_duration = forms.IntegerField(
        min_value=1,
        initial=5,
        label="Durée estimée (minutes)"
    )
    
    content_type = forms.CharField(
        widget=forms.HiddenInput(),
        initial="matching"
    )
    
    # Configuration de l'exercice
    difficulty = forms.ChoiceField(
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        initial="medium",
        label="Difficulté"
    )
    
    pairs_count = forms.IntegerField(
        min_value=4,
        max_value=20,
        initial=8,
        label="Nombre de paires",
        help_text="Nombre maximal de paires mot-traduction à afficher"
    )
    
    # Champ pour sélectionner du vocabulaire existant
    use_vocabulary = forms.BooleanField(
        required=False,
        initial=True,
        label="Utiliser du vocabulaire existant",
        help_text="Associe automatiquement du vocabulaire de la leçon"
    )
    
    def clean(self):
        # Validation personnalisée si nécessaire
        return super().clean()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm  # Conserve votre formulaire personnalisé
    
    # Améliorations des champs affichés
    list_display = (
        'id', 
        'get_title', 
        'get_unit_with_level',
        'lesson_type', 
        'get_professional_field', 
        'get_languages_status',
        'estimated_duration', 
        'order',
        'content_count',
    )
    
    # Filtres simples sans spécifier de classe
    list_filter = (
        'unit__level',  # Filtre simple par niveau
        'lesson_type',
        'unit',
        'professional_field',
        'estimated_duration',
    )
    
    # Recherche améliorée
    search_fields = (
        'title_en', 'title_fr', 'title_es', 'title_nl',
        'description_en', 'description_fr', 'description_es', 'description_nl',
        'unit__title_en',  # Recherche sur le titre de l'unité
    )
    
    # Ordre par défaut
    ordering = ('unit__level', 'unit__order', 'order')
    
    # Actions personnalisées
    actions = ['duplicate_lesson', 'export_as_csv', 'recalculate_duration']
    
    # Conserver vos inlines existants
    inlines = [ContentLessonInline]
    
    # Fonctions d'affichage améliorées
    def get_title(self, obj):
        """Afficher le titre en plusieurs langues"""
        return format_html(
            "<strong>{}</strong><br/>"
            "<small style='color:#666'>{} | {} | {}</small>",
            obj.title_en, 
            obj.title_fr, 
            obj.title_es, 
            obj.title_nl
        )
    get_title.short_description = 'Title (All Languages)'
    get_title.admin_order_field = 'title_en'
    
    def get_unit_with_level(self, obj):
        """Affiche l'unité avec son niveau et son ordre"""
        return format_html(
            "[{}] {} <br/><small>(ordre: {})</small>",
            obj.unit.level,
            obj.unit.title_en,
            obj.unit.order
        )
    get_unit_with_level.short_description = 'Unit'
    get_unit_with_level.admin_order_field = 'unit__level'
    
    def get_professional_field(self, obj):
        if obj.lesson_type == 'professional' and obj.professional_field:
            # Rendre le champ plus visible s'il est rempli
            return format_html('<span style="background:#e2f0d9; padding:3px 6px; border-radius:3px">{}</span>', obj.professional_field)
        return "-"
    get_professional_field.short_description = 'Professional Field'
    
    def get_languages_status(self, obj):
        """Indique si toutes les langues sont complètes pour cette leçon"""
        languages = ['en', 'fr', 'es', 'nl']
        status_html = []
        
        for lang_code in languages:
            title_field = f'title_{lang_code}'
            desc_field = f'description_{lang_code}'
            
            has_title = bool(getattr(obj, title_field))
            has_desc = bool(getattr(obj, desc_field))
            
            if has_title and has_desc:
                status = "✓"
                color = "green"
            elif has_title or has_desc:
                status = "~"
                color = "orange"
            else:
                status = "✗"
                color = "red"
                
            status_html.append(f'<span style="color:{color}">{lang_code.upper()}:{status}</span>')
        
        return format_html(' | '.join(status_html))
    get_languages_status.short_description = 'Languages'
    
    def content_count(self, obj):
        """Affiche le nombre de contenus avec indication visuelle"""
        count = obj.content_lessons.count()
        if count == 0:
            color = 'red'
        elif count < 3:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color:white; background-color:{0}; padding:3px 8px; border-radius:10px; font-weight:bold">{1}</span>',
            color, count
        )
    content_count.short_description = 'Contents'
    
    # Actions personnalisées (implémentations)
    def duplicate_lesson(self, request, queryset):
        """Action pour dupliquer les leçons sélectionnées"""
        count = 0
        for lesson in queryset:
            # Créer une copie de la leçon
            lesson_copy = Lesson.objects.create(
                unit=lesson.unit,
                lesson_type=lesson.lesson_type,
                professional_field=lesson.professional_field,
                title_en=f"Copy of {lesson.title_en}",
                title_fr=f"Copie de {lesson.title_fr}",
                title_es=f"Copia de {lesson.title_es}",
                title_nl=f"Kopie van {lesson.title_nl}",
                description_en=lesson.description_en,
                description_fr=lesson.description_fr,
                description_es=lesson.description_es,
                description_nl=lesson.description_nl,
                estimated_duration=lesson.estimated_duration,
                order=lesson.order + 1000  # Valeur temporaire élevée
            )
            count += 1
            
        # Message de confirmation
        self.message_user(request, f"{count} leçon(s) dupliquée(s) avec succès.")
        
        # Réordonner les leçons
        self._reorder_lessons(request)
    duplicate_lesson.short_description = "Dupliquer les leçons sélectionnées"

    def export_as_csv(self, request, queryset):
        """Exporte les leçons sélectionnées au format CSV avec plus de champs pour une meilleure gestion"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="lessons.csv"'
        
        writer = csv.writer(response)
        # En-têtes enrichis
        writer.writerow([
            'ID',
            'Title (EN)', 'Title (FR)', 'Title (ES)', 'Title (NL)',
            'Description (EN)', 'Description (FR)', 'Description (ES)', 'Description (NL)',
            'Unit ID', 'Unit Title', 'Unit Level', 'Unit Order',
            'Lesson Type',
        ])
        
        for lesson in queryset:
            # Récupérer le nombre de contenus et les types de contenus
            content_lessons = lesson.content_lessons.all()
            content_count = content_lessons.count()
            content_types = ', '.join(content_lessons.values_list('content_type', flat=True).distinct())
            
            # Statut des langues
            languages = ['en', 'fr', 'es', 'nl']
            lang_status = []
            for lang in languages:
                has_title = bool(getattr(lesson, f"title_{lang}", ""))
                has_desc = bool(getattr(lesson, f"description_{lang}", ""))
                if has_title and has_desc:
                    lang_status.append(f"{lang.upper()}:✓")
                elif has_title or has_desc:
                    lang_status.append(f"{lang.upper()}:~")
                else:
                    lang_status.append(f"{lang.upper()}:✗")
            
            writer.writerow([
                lesson.id,
                lesson.title_en, lesson.title_fr, lesson.title_es, lesson.title_nl,
                lesson.description_en, lesson.description_fr, lesson.description_es, lesson.description_nl,
                lesson.unit.id if lesson.unit else '',
                lesson.unit.title_en if lesson.unit else '',
                lesson.unit.level if lesson.unit else '',
                lesson.unit.order if lesson.unit else '',
                lesson.lesson_type, 
                ', '.join(lang_status),
                content_types
            ])
        
        return response
    export_as_csv.short_description = "Exporter en CSV (détaillé)"
    def recalculate_duration(self, request, queryset):
        """Recalcule la durée estimée en fonction des content lessons"""
        updated = 0
        for lesson in queryset:
            old_duration = lesson.estimated_duration
            # Force le recalcul de la durée via la méthode save()
            lesson.save()
            if old_duration != lesson.estimated_duration:
                updated += 1
                
        self.message_user(
            request, 
            f"Durée recalculée pour {updated} leçon(s) sur {queryset.count()} sélectionnée(s)."
        )
    recalculate_duration.short_description = "Recalculer la durée estimée"
    
    def _reorder_lessons(self, request):
        """Réordonne les leçons pour chaque unité"""
        # Obtenir toutes les unités avec des leçons
        units = Unit.objects.filter(lessons__isnull=False).distinct()
        
        for unit in units:
            # Obtenir toutes les leçons de cette unité
            lessons = Lesson.objects.filter(unit=unit).order_by('order')
            
            # Réordonner les leçons
            for i, lesson in enumerate(lessons, 1):
                if lesson.order != i:
                    lesson.order = i
                    lesson.save(update_fields=['order'])
    
    # Style et ressources additionnelles
    class Media:
        js = ('js/lesson_admin.js',)
        css = {
            'all': ('css/lesson_admin.css',)
        }
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/create-matching/',
                 self.admin_site.admin_view(self.create_matching_view),
                 name='course_lesson_create_matching'),
        ]
        return custom_urls + urls
    
    def create_matching_view(self, request, object_id):
        """Vue pour créer rapidement un exercice de matching associé à une leçon"""
        # Récupérer la leçon
        lesson = get_object_or_404(Lesson, pk=object_id)
        
        # Contexte initial
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Créer un exercice de matching pour {lesson.title_en}',
            'lesson': lesson,
            'form': None,
            'has_vocab': VocabularyList.objects.filter(
                content_lesson__lesson=lesson
            ).exists(),
            'vocab_count': VocabularyList.objects.filter(
                content_lesson__lesson=lesson
            ).count(),
        }
        
        if request.method == 'POST':
            form = QuickMatchingExerciseForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # 1. Créer le ContentLesson
                        content_lesson = ContentLesson.objects.create(
                            lesson=lesson,
                            content_type=form.cleaned_data['content_type'],
                            title_en=form.cleaned_data['title_en'],
                            title_fr=form.cleaned_data['title_fr'],
                            title_es=form.cleaned_data['title_es'],
                            title_nl=form.cleaned_data['title_nl'],
                            instruction_en=form.cleaned_data['instruction_en'],
                            instruction_fr=form.cleaned_data['instruction_fr'],
                            instruction_es=form.cleaned_data['instruction_es'],
                            instruction_nl=form.cleaned_data['instruction_nl'],
                            estimated_duration=form.cleaned_data['estimated_duration'],
                            order=ContentLesson.objects.filter(lesson=lesson).count() + 1
                        )
                        
                        # 2. Créer le MatchingExercise
                        exercise = MatchingExercise.objects.create(
                            content_lesson=content_lesson,
                            difficulty=form.cleaned_data['difficulty'],
                            title_en=form.cleaned_data['title_en'],
                            title_fr=form.cleaned_data['title_fr'],
                            title_es=form.cleaned_data['title_es'],
                            title_nl=form.cleaned_data['title_nl'],
                            pairs_count=form.cleaned_data['pairs_count'],
                            order=1  # Premier exercice pour ce ContentLesson
                        )
                        
                        # 3. Associer automatiquement le vocabulaire si demandé
                        if form.cleaned_data['use_vocabulary']:
                            # Trouver le vocabulaire disponible
                            vocabulary_items = VocabularyList.objects.filter(
                                content_lesson__lesson=lesson
                            )[:form.cleaned_data['pairs_count']]
                            
                            if vocabulary_items.exists():
                                # Ajouter le vocabulaire trouvé à l'exercice
                                for vocab in vocabulary_items:
                                    exercise.vocabulary_words.add(vocab)
                    
                    # Afficher un message de succès
                    messages.success(
                        request,
                        f"L'exercice '{form.cleaned_data['title_en']}' a été créé avec succès."
                    )
                    
                    # Rediriger vers la page d'édition du MatchingExercise
                    return redirect('admin:course_matchingexercise_change', exercise.id)
                    
                except Exception as e:
                    messages.error(request, f"Erreur lors de la création: {str(e)}")
        else:
            # Formulaire initial avec leçon pré-sélectionnée
            form = QuickMatchingExerciseForm(initial={
                'lesson': lesson,
            })
            context['form'] = form
        
        return TemplateResponse(request, 'admin/course/create_matching_exercise.html', context)

class VocabularyInline(admin.TabularInline):
    model = SpeakingExercise.vocabulary_items.through
    verbose_name = "Vocabulary Item"
    verbose_name_plural = "Vocabulary Items"
    extra = 1
    autocomplete_fields = ['vocabularylist']


@admin.register(SpeakingExercise)
class SpeakingExerciseAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_lesson_info', 'vocabulary_count', 'content_lesson_id']
    list_filter = ['content_lesson__lesson__unit__level']
    search_fields = ['content_lesson__title_en']

    fieldsets = [
        (None, {
            'fields': ['content_lesson']
        }),
    ]
    inlines = [VocabularyInline]
    exclude = ['vocabulary_items']  # Exclu car géré par l'inline
    
    def exercise_title(self, obj):
        return obj.title_en
    exercise_title.short_description = "Title"
    
    def content_lesson_info(self, obj):
        unit_info = obj.content_lesson.lesson.unit.title_en
        lesson_info = obj.content_lesson.lesson.title_en
        return format_html(
            "<strong>Unit:</strong> {} <br/><strong>Lesson:</strong> {}",
            unit_info, lesson_info
        )
    content_lesson_info.short_description = "Lesson Info"
    
    def vocabulary_count(self, obj):
        count = obj.vocabulary_items.count()
        return format_html(
            '<span style="color:{}">{} items</span>',
            'green' if count > 0 else 'red',
            count
        )
    vocabulary_count.short_description = "Vocabulary"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'content_lesson__lesson__unit'
        ).prefetch_related('vocabulary_items')

    actions = ['associate_vocabulary_from_lesson']
    
    def associate_vocabulary_from_lesson(self, request, queryset):
        """Action qui associe automatiquement tous les mots de vocabulaire pertinents aux exercices sélectionnés"""
        total_exercises = queryset.count()
        exercises_updated = 0
        words_added = 0
        
        for exercise in queryset:
            content_lesson = exercise.content_lesson
            parent_lesson = content_lesson.lesson
            
            # Mémoriser le nombre de mots avant l'opération
            words_before = exercise.vocabulary_items.count()
            
            # 1. Essayer de trouver des mots dans la même content_lesson
            vocab_items = VocabularyList.objects.filter(content_lesson=content_lesson)
            
            # 2. Si aucun mot, chercher dans les content_lessons de type vocabulaire dans la même lesson
            if not vocab_items.exists():
                vocab_lessons = ContentLesson.objects.filter(
                    lesson=parent_lesson,
                    content_type__iexact='vocabulary'
                )
                
                for vocab_lesson in vocab_lessons:
                    lesson_vocab = VocabularyList.objects.filter(content_lesson=vocab_lesson)
                    vocab_items = vocab_items | lesson_vocab
            
            # Associer tous les mots trouvés
            if vocab_items.exists():
                exercise.vocabulary_items.add(*vocab_items)
                exercises_updated += 1
                
                # Calculer combien de mots ont été ajoutés
                words_after = exercise.vocabulary_items.count()
                words_added += (words_after - words_before)
        
        # Message de confirmation
        if exercises_updated:
            message = f"✓ {words_added} vocabulary items added to {exercises_updated} speaking exercises."
        else:
            message = "No vocabulary items found for the selected exercises."
            
        self.message_user(request, message)
        
    associate_vocabulary_from_lesson.short_description = "Associate vocabulary items from lessons"


class TheoryContentAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour l'édition des contenus théoriques"""
    
    language_specific_content = AdminJSONFormField(
        label="Contenu spécifique par langue",
        help_text="Contenu pour chaque langue (format JSON structuré)"
    )
    
    class Meta:
        model = TheoryContent
        fields = '__all__'
        
    def clean_language_specific_content(self):
        """Validation et formatage automatique du JSON"""
        data = self.cleaned_data['language_specific_content']
        
        # Vérifier que la structure est correcte
        required_fields = ['content', 'explanation']
        
        for lang, content in data.items():
            if not isinstance(content, dict):
                raise forms.ValidationError(f"Le contenu pour la langue '{lang}' doit être un objet JSON.")
            
            # Vérifier la présence des champs obligatoires
            for field in required_fields:
                if field not in content:
                    raise forms.ValidationError(f"Champ '{field}' manquant pour la langue '{lang}'")
        
        return data

@admin.register(TheoryContent)
class TheoryContentAdmin(admin.ModelAdmin):
    form = TheoryContentAdminForm
    list_display = ('id', 'get_content_title', 'has_formula', 'has_examples', 'format_indicator', 'language_count')
    list_filter = ('content_lesson__lesson__unit', 'using_json_format')
    search_fields = ('content_en', 'content_fr', 'content_lesson__title_en', 'language_specific_content')
    actions = ['migrate_to_json_format', 'add_custom_language']
    
    class Media:
        css = {
            'all': ('css/codemirror.css', 'css/language_editor.css')
        }
        js = ('js/codemirror.js', 'js/codemirror-mode-javascript.js', 'js/language_editor.js')
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Initialiser le contenu JSON si c'est un nouvel enregistrement et le format JSON est activé
        if not obj and request.method == 'POST' and request.POST.get('using_json_format') == 'on':
            # Structure JSON par défaut avec les champs requis
            form.base_fields['language_specific_content'].initial = {
                "en": {"content": "", "explanation": ""},
                "fr": {"content": "", "explanation": ""},
                "es": {"content": "", "explanation": ""},
                "nl": {"content": "", "explanation": ""}
            }
            form.base_fields['available_languages'].initial = ["en", "fr", "es", "nl"]
        
        return form
    def get_fieldsets(self, request, obj=None):
        """Affiche différents fieldsets selon que l'objet utilise le format JSON ou non"""
        base_fieldsets = [
            ('Lesson Reference', {
                'fields': ('content_lesson',)
            }),
        ]
        
        # Déterminer si nous utilisons JSON - vérifier à la fois l'objet et les données POST
        using_json_format = False
        
        # Vérifier si c'est une édition d'un objet existant utilisant JSON
        if obj and obj.using_json_format:
            using_json_format = True
        
        # Vérifier si c'est un nouvel objet avec JSON sélectionné
        elif request.method == 'POST' and 'using_json_format' in request.POST:
            using_json_format = request.POST.get('using_json_format') == 'on'
        
        # Si le format JSON est activé (nouveau ou existant)
        if using_json_format:
            json_fieldsets = [
                ('Format Settings', {
                    'fields': ('using_json_format', 'available_languages'),
                    'classes': ('collapse',),
                }),
                ('Language Specific Content (JSON Format)', {
                    'fields': ('language_specific_content',),
                    'description': 'This content is in JSON format. Edit with caution.',
                }),
            ]
            
            # Ajouter la prévisualisation seulement pour les objets existants
            if obj:
                json_fieldsets.append(
                    ('Content Preview', {
                        'fields': ('content_preview',),
                        'classes': ('collapse',),
                    })
                )
                
            return base_fieldsets + json_fieldsets
        
        # Sinon, afficher les champs traditionnels
        traditional_fieldsets = [
            ('Format Options', {
                'fields': ('using_json_format',),
                'description': 'Enable JSON format for more flexible language support.'
            }),
            ('English Content', {
                'fields': ('content_en', 'explication_en', 'formula_en', 'example_en', 'exception_en'),
            }),
            ('French Content', {
                'fields': ('content_fr', 'explication_fr', 'formula_fr', 'example_fr', 'exception_fr'),
            }),
            ('Spanish Content', {
                'fields': ('content_es', 'explication_es', 'formula_es', 'example_es', 'exception_es'),
            }),
            ('Dutch Content', {
                'fields': ('content_nl', 'explication_nl', 'formula_nl', 'example_nl', 'exception_nl'),
            }),
        ]
        return base_fieldsets + traditional_fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        """Définit les champs en lecture seule selon le format utilisé"""
        readonly_fields = ['content_preview']
        
        # Vérifier si nous utilisons JSON (en édition ou en création)
        using_json_format = False
        
        if obj and obj.using_json_format:
            using_json_format = True
        elif request.method == 'POST' and request.POST.get('using_json_format') == 'on':
            using_json_format = True
        
        # Si format JSON, tous les champs traditionnels sont en lecture seule
        if using_json_format:
            readonly_fields.extend([
                'content_en', 'content_fr', 'content_es', 'content_nl',
                'explication_en', 'explication_fr', 'explication_es', 'explication_nl',
                'formula_en', 'formula_fr', 'formula_es', 'formula_nl',
                'example_en', 'example_fr', 'example_es', 'example_nl',
                'exception_en', 'exception_fr', 'exception_es', 'exception_nl'
            ])
        
        return readonly_fields
    
    def get_content_title(self, obj):
        return obj.content_lesson.title_en
    get_content_title.short_description = 'Content Title'
    
    def has_formula(self, obj):
        """Vérifie si la théorie a des formules (nouveau ou ancien format)"""
        if obj.using_json_format:
            # Vérifier dans le format JSON
            for lang_data in obj.language_specific_content.values():
                if lang_data.get('formula'):
                    return True
            return False
        # Ancien format
        return bool(obj.formula_en or obj.formula_fr or obj.formula_es or obj.formula_nl)
    has_formula.boolean = True
    
    def has_examples(self, obj):
        """Vérifie si la théorie a des exemples (nouveau ou ancien format)"""
        if obj.using_json_format:
            # Vérifier dans le format JSON
            for lang_data in obj.language_specific_content.values():
                if lang_data.get('example'):
                    return True
            return False
        # Ancien format
        return bool(obj.example_en or obj.example_fr or obj.example_es or obj.example_nl)
    has_examples.boolean = True
    
    def format_indicator(self, obj):
        """Indique quel format est utilisé"""
        if obj.using_json_format:
            return "JSON Format ✓"
        return "Traditional Format"
    format_indicator.short_description = "Format"
    
    def language_count(self, obj):
        """Affiche le nombre de langues disponibles"""
        if obj.using_json_format:
            return len(obj.available_languages)
        # Compter les langues disponibles dans l'ancien format
        count = 0
        for lang in ['en', 'fr', 'es', 'nl']:
            if getattr(obj, f'content_{lang}'):
                count += 1
        return count
    language_count.short_description = "Languages"
    
    def content_preview(self, obj):
        """Champ virtuel pour afficher un aperçu du contenu dans différentes langues"""
        if not obj.using_json_format:
            return "Switch to JSON format to see content preview"
        
        html = ['<div style="max-height: 400px; overflow-y: auto;">']
        
        for lang in obj.available_languages:
            lang_data = obj.language_specific_content.get(lang, {})
            
            html.append(f'<h3 style="margin-top: 15px; padding: 5px; background-color: #f5f5f5;">{lang.upper()}</h3>')
            
            # Content
            if 'content' in lang_data:
                html.append(f'<p><strong>Content:</strong> {lang_data["content"]}</p>')
            
            # Explanation
            if 'explanation' in lang_data:
                html.append(f'<p><strong>Explanation:</strong> {lang_data["explanation"]}</p>')
            
            # Formula
            if 'formula' in lang_data:
                html.append(f'<p><strong>Formula:</strong> {lang_data["formula"]}</p>')
            
            # Example
            if 'example' in lang_data:
                html.append(f'<p><strong>Example:</strong> {lang_data["example"]}</p>')
            
            # Exception
            if 'exception' in lang_data:
                html.append(f'<p><strong>Exception:</strong> {lang_data["exception"]}</p>')
            
            # Language-specific fields
            for key, value in lang_data.items():
                if key not in ['content', 'explanation', 'formula', 'example', 'exception']:
                    html.append(f'<p><strong>{key}:</strong> {value}</p>')
            
            html.append('<hr>')
        
        html.append('</div>')
        return mark_safe(''.join(html))
    content_preview.short_description = "Content Preview"
    
    # Actions personnalisées
    @admin.action(description="Migrer vers le format JSON")
    def migrate_to_json_format(self, request, queryset):
        """Action pour migrer les théories vers le format JSON"""
        migrated = 0
        for theory in queryset:
            if not theory.using_json_format:
                theory.migrate_to_json_format()
                migrated += 1
        
        self.message_user(
            request,
            f"{migrated} théories ont été migrées avec succès vers le format JSON.",
            messages.SUCCESS
        )
    
    @admin.action(description="Ajouter une langue personnalisée")
    def add_custom_language(self, request, queryset):
        """Action pour ajouter une langue personnalisée"""
        # Cette action nécessiterait un formulaire personnalisé
        # qui demanderait le code de langue et les données à ajouter
        # Exemple simplifié:
        if queryset.count() != 1:
            self.message_user(
                request,
                "Veuillez sélectionner une seule théorie pour ajouter une langue.",
                messages.ERROR
            )
            return
        
        theory = queryset.first()
        
        # Rediriger vers une vue personnalisée qui affichera un formulaire
        return HttpResponseRedirect(
            reverse('admin:add_custom_language', args=[theory.pk])
        )
    
    # Surcharger get_urls pour ajouter des vues personnalisées
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/add-language/',
                self.admin_site.admin_view(self.add_language_view),
                name='add_custom_language',
            ),
        ]
        return custom_urls + urls
    
    def add_language_view(self, request, object_id):
        """Vue personnalisée pour ajouter une langue à une théorie"""
        theory = get_object_or_404(TheoryContent, pk=object_id)
        
        if request.method == 'POST':
            language_code = request.POST.get('language_code')
            content = request.POST.get('content')
            explanation = request.POST.get('explanation')
            formula = request.POST.get('formula', '')
            example = request.POST.get('example', '')
            exception = request.POST.get('exception', '')
            
            # Validation basique
            if not language_code or not content or not explanation:
                messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            elif len(language_code) != 2:
                messages.error(request, "Le code de langue doit être de 2 caractères (ex: 'fr', 'en').")
            else:
                # Créer/mettre à jour le contenu JSON
                if not theory.using_json_format:
                    theory.migrate_to_json_format()
                
                # Ajouter ou mettre à jour la langue
                current_content = theory.language_specific_content.copy() if theory.language_specific_content else {}
                
                current_content[language_code] = {
                    'content': content,
                    'explanation': explanation,
                    'formula': formula,
                    'example': example,
                    'exception': exception
                }
                
                # Mettre à jour les langues disponibles
                available_languages = theory.available_languages.copy() if theory.available_languages else []
                if language_code not in available_languages:
                    available_languages.append(language_code)
                
                # Sauvegarder les modifications
                theory.language_specific_content = current_content
                theory.available_languages = available_languages
                theory.save()
                
                messages.success(request, f"Langue '{language_code}' ajoutée avec succès!")
                return redirect('admin:course_theorycontent_change', object_id=theory.pk)
        
        # Template context
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Ajouter une langue à la théorie #{object_id}',
            'theory': theory,
            'available_languages': [
                {'code': 'en', 'name': 'Anglais'},
                {'code': 'fr', 'name': 'Français'},
                {'code': 'es', 'name': 'Espagnol'},
                {'code': 'nl', 'name': 'Néerlandais'},
                {'code': 'de', 'name': 'Allemand'},
                {'code': 'it', 'name': 'Italien'},
                {'code': 'pt', 'name': 'Portugais'},
            ]
        }
        
        return TemplateResponse(request, 'admin/add_language_form.html', context)

@admin.register(VocabularyList)
class VocabularyListAdmin(admin.ModelAdmin):
    list_display = ('id', 'word_en', 'word_fr', 'word_type_en', 'content_lesson')
    list_filter = ('content_lesson__lesson__unit', 'word_type_en')
    search_fields = ('word_en', 'word_fr', 'definition_en')
    fieldsets = (
        ('Lesson Reference', {
            'fields': ('content_lesson',)
        }),
        ('English', {
            'fields': ('word_en', 'definition_en', 'example_sentence_en', 'word_type_en', 'synonymous_en', 'antonymous_en'),
        }),
        ('French', {
            'fields': ('word_fr', 'definition_fr', 'example_sentence_fr', 'word_type_fr', 'synonymous_fr', 'antonymous_fr'),
        }),
        ('Spanish', {
            'fields': ('word_es', 'definition_es', 'example_sentence_es', 'word_type_es', 'synonymous_es', 'antonymous_es'),
        }),
        ('Dutch', {
            'fields': ('word_nl', 'definition_nl', 'example_sentence_nl', 'word_type_nl', 'synonymous_nl', 'antonymous_nl'),
        }),
    )


@admin.register(Numbers)
class NumbersAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'number_en', 'number_fr', 'is_reviewed', 'content_lesson')
    list_filter = ('is_reviewed', 'content_lesson__lesson__unit')
    search_fields = ('number', 'number_en', 'number_fr')
    list_editable = ('is_reviewed',)


@admin.register(MatchingExercise)
class MatchingExerciseAdmin(admin.ModelAdmin):
    """Interface d'administration pour les exercices d'association."""
    
    change_list_template = 'admin/course/matchingexercise/change_list.html'
    
    def changelist_view(self, request, extra_context=None):
        # Ajouter le url pour la création rapide
        extra_context = extra_context or {}
        extra_context['quick_create_url'] = reverse('admin:matchingexercise_quick_create')
        return super().changelist_view(request, extra_context=extra_context)
    
    # Affichage dans la liste
    list_display = ('id', 'get_title_display', 'get_pairs_display', 'get_status_display', 'difficulty', 'pairs_count', 'order')
    list_filter = ('difficulty', 'content_lesson__lesson__unit__level', PairsStatusFilter, PairsCountRangeFilter, 'pairs_count')
    search_fields = ('title_en', 'title_fr', 'content_lesson__title_en')
    list_editable = ('pairs_count', 'order')
    
    # Mise en page du formulaire
    fieldsets = (
        ('Informations de base', {
            'fields': ('content_lesson', 'difficulty', 'order')
        }),
        ('Titres multilingues', {
            'fields': ('title_en', 'title_fr', 'title_es', 'title_nl'),
            'description': 'Les titres peuvent être personnalisés pour chaque exercice.',
            'classes': ('collapse',)
        }),
        ('Configuration des paires', {
            'fields': ('pairs_count', 'preview_vocabulary_pairs', 'vocabulary_words'),
            'description': 'Configurez le nombre de paires et sélectionnez le vocabulaire.'
        }),
    )
    
    readonly_fields = ('preview_vocabulary_pairs', 'get_pairs_display', 'get_status_display')
    
    # Relations
    filter_horizontal = ('vocabulary_words',)
    
    def get_content_lesson_title(self, obj):
        """Affiche le titre de la leçon associée pour faciliter l'identification."""
        return obj.content_lesson.title_en
    get_content_lesson_title.short_description = 'Leçon'
    get_content_lesson_title.admin_order_field = 'content_lesson__title_en'
    
    def get_vocab_count(self, obj):
        """Affiche le nombre réel de mots de vocabulaire associés."""
        count = obj.vocabulary_words.count()
        if count != obj.pairs_count:
            return format_html('<span style="color: red;">{}</span>', count)
        return count
    get_vocab_count.short_description = 'Vocab réel'
    
    def get_title_display(self, obj):
        """Affiche le titre avec la leçon parente pour plus de clarté."""
        lesson_title = obj.content_lesson.lesson.title_en if obj.content_lesson and obj.content_lesson.lesson else "N/A"
        return format_html(
            '<strong>{}</strong><br/><small style="color: #666;">Lesson: {}</small>',
            obj.title_en or "Sans titre",
            lesson_title
        )
    get_title_display.short_description = 'Titre'
    
    def get_pairs_display(self, obj):
        """Affiche visuellement le nombre de paires configuré vs réel."""
        actual_count = obj.vocabulary_words.count()
        configured_count = obj.pairs_count
        
        if actual_count == configured_count:
            color = "green"
            status = "✓"
        elif actual_count < configured_count:
            color = "orange"
            status = "⚠"
        else:
            color = "blue"
            status = "↑"
            
        return format_html(
            '<div style="text-align: center;">'
            '<span style="font-size: 20px; color: {};">{}</span><br/>'
            '<strong>{}/{}</strong><br/>'
            '<small>Réel/Configuré</small>'
            '</div>',
            color, status, actual_count, configured_count
        )
    get_pairs_display.short_description = 'Paires'
    get_pairs_display.admin_order_field = 'pairs_count'
    
    def get_status_display(self, obj):
        """Affiche le statut visuel de l'exercice."""
        actual_count = obj.vocabulary_words.count()
        configured_count = obj.pairs_count
        
        if actual_count == 0:
            return format_html('<span style="color: red;">❌ Aucune paire</span>')
        elif actual_count < configured_count:
            return format_html('<span style="color: orange;">⚠️ Incomplet ({}/{})</span>', actual_count, configured_count)
        elif actual_count == configured_count:
            return format_html('<span style="color: green;">✅ Complet</span>')
        else:
            return format_html('<span style="color: blue;">↑ Excès ({}/{})</span>', actual_count, configured_count)
    get_status_display.short_description = 'Statut'
    
    def preview_vocabulary_pairs(self, obj):
        """Prévisualise les paires de vocabulaire dans le formulaire."""
        vocab_items = obj.vocabulary_words.all()[:5]  # Limite à 5 pour la prévisualisation
        
        if not vocab_items:
            return "Aucune paire configurée"
        
        pairs_html = []
        for item in vocab_items:
            pairs_html.append(
                f'<div style="margin: 5px 0; padding: 5px; background: #f0f0f0; border-radius: 3px;">'
                f'<strong>{item.word_fr}</strong> ↔ <strong>{item.word_en}</strong>'
                f'</div>'
            )
        
        if obj.vocabulary_words.count() > 5:
            pairs_html.append(f'<div style="color: #666; font-style: italic;">... et {obj.vocabulary_words.count() - 5} autres paires</div>')
        
        return format_html(''.join(pairs_html))
    preview_vocabulary_pairs.short_description = 'Aperçu des paires'
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Filtre les mots disponibles en fonction de la leçon sélectionnée,
        pour simplifier la création des exercices.
        """
        if db_field.name == 'vocabulary_words':
            # Vérifier si request._obj existe (défini dans get_form)
            if hasattr(request, '_obj') and request._obj is not None:
                kwargs['queryset'] = VocabularyList.objects.filter(
                    content_lesson=request._obj.content_lesson
                )
            elif 'content_lesson' in request.GET:
                content_lesson_id = request.GET.get('content_lesson')
                kwargs['queryset'] = VocabularyList.objects.filter(
                    content_lesson_id=content_lesson_id
                )
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        """Conserve une référence à l'objet en cours d'édition pour le filtrage."""
        request._obj = obj
        return super().get_form(request, obj, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        """
        Personnalise la vue d'ajout pour inclure des informations supplémentaires
        sur les instructions standardisées.
        """
        extra_context = extra_context or {}
        extra_context['instructions_note'] = (
            "Les instructions d'utilisation sont standardisées et identiques "
            "pour tous les exercices d'association, conformément aux exigences pédagogiques."
        )
        return super().add_view(request, form_url, extra_context)
    
    actions = ['associate_vocabulary_from_lesson', 'split_large_exercises', 'optimize_pairs_count', 'check_pairs_consistency']
    
    def associate_vocabulary_from_lesson(self, request, queryset):
        """Action to automatically associate all relevant vocabulary with selected matching exercises"""
        total_exercises = queryset.count()
        exercises_updated = 0
        words_added = 0
        
        for exercise in queryset:
            content_lesson = exercise.content_lesson
            parent_lesson = content_lesson.lesson
            
            # Memorize the number of words before the operation
            words_before = exercise.vocabulary_words.count()
            
            # 1. Try to find vocabulary in the same content lesson
            vocab_items = VocabularyList.objects.filter(content_lesson=content_lesson)
            
            # 2. If no words, look in vocabulary content lessons in the same lesson
            if not vocab_items.exists():
                vocab_lessons = ContentLesson.objects.filter(
                    lesson=parent_lesson,
                    content_type__iexact='vocabulary'
                )
                
                for vocab_lesson in vocab_lessons:
                    lesson_vocab = VocabularyList.objects.filter(content_lesson=vocab_lesson)
                    if vocab_items.exists():
                        vocab_items = vocab_items | lesson_vocab
                    else:
                        vocab_items = lesson_vocab
            
            # Associate all found words, limited by pairs_count
            if vocab_items.exists():
                # Limit to the pairs_count specified in the exercise
                vocab_items = vocab_items[:exercise.pairs_count]
                exercise.vocabulary_words.add(*vocab_items)
                exercises_updated += 1
                
                # Calculate how many words were added
                words_after = exercise.vocabulary_words.count()
                words_added += (words_after - words_before)
        
        # Confirmation message
        if exercises_updated:
            message = f"✓ {words_added} vocabulary items added to {exercises_updated} matching exercises."
        else:
            message = "No vocabulary items found for the selected exercises."
            
        self.message_user(request, message)
        
    associate_vocabulary_from_lesson.short_description = "Associate vocabulary items from lessons"
    
    def split_large_exercises(self, request, queryset):
        """Divise les exercices avec trop de paires en plusieurs exercices plus petits."""
        from math import ceil
        
        created_count = 0
        for exercise in queryset:
            vocab_count = exercise.vocabulary_words.count()
            if vocab_count > exercise.pairs_count:
                # Calculer le nombre d'exercices nécessaires
                num_exercises = ceil(vocab_count / exercise.pairs_count)
                vocabulary_items = list(exercise.vocabulary_words.all())
                
                # Créer des exercices supplémentaires
                for i in range(1, num_exercises):
                    new_exercise = MatchingExercise.objects.create(
                        content_lesson=exercise.content_lesson,
                        title_en=f"{exercise.title_en} - Part {i+1}",
                        title_fr=f"{exercise.title_fr} - Partie {i+1}",
                        title_es=f"{exercise.title_es} - Parte {i+1}",
                        title_nl=f"{exercise.title_nl} - Deel {i+1}",
                        pairs_count=exercise.pairs_count,
                        difficulty=exercise.difficulty,
                        order=exercise.order + i
                    )
                    
                    # Associer le vocabulaire approprié
                    start_idx = i * exercise.pairs_count
                    end_idx = min((i + 1) * exercise.pairs_count, vocab_count)
                    new_exercise.vocabulary_words.set(vocabulary_items[start_idx:end_idx])
                    created_count += 1
                
                # Mettre à jour l'exercice original
                exercise.title_en = f"{exercise.title_en} - Part 1"
                exercise.title_fr = f"{exercise.title_fr} - Partie 1"
                exercise.title_es = f"{exercise.title_es} - Parte 1"
                exercise.title_nl = f"{exercise.title_nl} - Deel 1"
                exercise.vocabulary_words.set(vocabulary_items[:exercise.pairs_count])
                exercise.save()
        
        if created_count:
            self.message_user(request, f"✅ {created_count} nouveaux exercices créés par division")
        else:
            self.message_user(request, "ℹ️ Aucun exercice n'a besoin d'être divisé")
    
    split_large_exercises.short_description = "Diviser les exercices avec trop de paires"
    
    def optimize_pairs_count(self, request, queryset):
        """Ajuste automatiquement pairs_count pour correspondre au vocabulaire disponible."""
        optimized_count = 0
        
        for exercise in queryset:
            vocab_count = exercise.vocabulary_words.count()
            if vocab_count != exercise.pairs_count and vocab_count > 0:
                exercise.pairs_count = vocab_count
                exercise.save()
                optimized_count += 1
        
        if optimized_count:
            self.message_user(request, f"✅ {optimized_count} exercices optimisés")
        else:
            self.message_user(request, "ℹ️ Tous les exercices sont déjà optimisés")
    
    optimize_pairs_count.short_description = "Optimiser le nombre de paires"
    
    def check_pairs_consistency(self, request, queryset):
        """Vérifie la cohérence des paires et signale les problèmes."""
        issues = []
        
        for exercise in queryset:
            vocab_count = exercise.vocabulary_words.count()
            pairs_count = exercise.pairs_count
            
            if vocab_count == 0:
                issues.append(f"❌ {exercise.title_en}: Aucune paire définie")
            elif vocab_count < pairs_count:
                issues.append(f"⚠️ {exercise.title_en}: {vocab_count}/{pairs_count} paires (incomplet)")
            elif vocab_count > pairs_count:
                issues.append(f"↑ {exercise.title_en}: {vocab_count}/{pairs_count} paires (excès)")
            else:
                issues.append(f"✅ {exercise.title_en}: {vocab_count} paires (correct)")
        
        if issues:
            message = "Rapport de cohérence des paires:<br/>" + "<br/>".join(issues)
            self.message_user(request, format_html(message))
        else:
            self.message_user(request, "✅ Tous les exercices sont cohérents")
    
    check_pairs_consistency.short_description = "Vérifier la cohérence des paires"


@admin.register(MultipleChoiceQuestion)
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_en', 'correct_answer_en', 'content_lesson')
    list_filter = ('content_lesson__lesson__unit',)
    search_fields = ('question_en', 'question_fr')
    fieldsets = (
        ('Lesson Reference', {
            'fields': ('content_lesson',)
        }),
        ('English', {
            'fields': ('question_en', 'correct_answer_en', 'fake_answer1_en', 'fake_answer2_en', 
                      'fake_answer3_en', 'fake_answer4_en', 'hint_answer_en'),
        }),
        ('French', {
            'fields': ('question_fr', 'correct_answer_fr', 'fake_answer1_fr', 'fake_answer2_fr', 
                      'fake_answer3_fr', 'fake_answer4_fr', 'hint_answer_fr'),
        }),
        ('Spanish', {
            'fields': ('question_es', 'correct_answer_es', 'fake_answer1_es', 'fake_answer2_es', 
                      'fake_answer3_es', 'fake_answer4_es', 'hint_answer_es'),
        }),
        ('Dutch', {
            'fields': ('question_nl', 'correct_answer_nl', 'fake_answer1_nl', 'fake_answer2_nl', 
                      'fake_answer3_nl', 'fake_answer4_nl', 'hint_answer_nl'),
        }),
    )


@admin.register(ExerciseGrammarReordering)
class ExerciseGrammarReorderingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sentence_en', 'content_lesson')
    list_filter = ('content_lesson__lesson__unit',)
    search_fields = ('sentence_en', 'sentence_fr')
    fieldsets = (
        ('Lesson Reference', {
            'fields': ('content_lesson',)
        }),
        ('Sentence Variations', {
            'fields': ('sentence_en', 'sentence_fr', 'sentence_es', 'sentence_nl'),
        }),
        ('Help Text', {
            'fields': ('explanation', 'hint'),
        }),
    )


@admin.register(ExerciseVocabularyMultipleChoice)
class ExerciseVocabularyMultipleChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer', 'lesson')
    list_filter = ('lesson__unit',)
    search_fields = ('question', 'correct_answer')


class FillBlankExerciseAdminForm(forms.ModelForm):
    """Enhanced custom form for Fill in the Blank exercises admin"""
    
    instructions = AdminJSONFormField(
        label="Instructions",
        help_text="Instructions for each language (e.g. 'Select the right word')"
    )
    
    sentences = AdminJSONFormField(
        label="Sentences with Blanks",
        help_text="Use ___ to mark where the blank should appear (e.g. 'Paris is ___ in France.')"
    )
    
    answer_options = AdminJSONFormField(
        label="Answer Options",
        help_text="List of possible answers for each language"
    )
    
    correct_answers = AdminJSONFormField(
        label="Correct Answers",
        help_text="The correct answer for each language"
    )
    
    hints = AdminJSONFormField(
        label="Hints",
        help_text="Optional hints to help users (shown when they're stuck)",
        required=False
    )
    
    explanations = AdminJSONFormField(
        label="Explanations",
        help_text="Explanations why the answer is correct (shown after answering)",
        required=False
    )
    
    tags = AdminJSONFormField(
        label="Tags",
        help_text="Tags for categorizing this exercise (e.g. ['grammar', 'beginner'])",
        required=False
    )
    
    class Meta:
        model = FillBlankExercise
        fields = '__all__'

    def clean(self):
        """Advanced validation to ensure consistency"""
        cleaned_data = super().clean()
        
        sentences = cleaned_data.get('sentences', {})
        answer_options = cleaned_data.get('answer_options', {})
        correct_answers = cleaned_data.get('correct_answers', {})
        
        errors = []
        
        # For each language, verify that:
        # 1. The sentence contains the blank marker
        # 2. The correct answer is in the options list
        # 3. The blank can fit the longest option reasonably
        for lang in sentences.keys():
            sentence = sentences.get(lang, '')
            options = answer_options.get(lang, [])
            correct = correct_answers.get(lang, '')
            
            if '___' not in sentence:
                errors.append(f"The sentence for language '{lang}' does not contain a blank (___)")
            
            if options and correct and correct not in options:
                errors.append(f"The correct answer '{correct}' for language '{lang}' is not in the options list")
            
            if options:
                max_option_len = max([len(opt) for opt in options]) if options else 0
                if max_option_len > 50:  # Arbitrary threshold for very long options
                    errors.append(f"Some options for language '{lang}' are very long. Consider shortening them.")
        
        if errors:
            raise forms.ValidationError(errors)
            
        return cleaned_data


@admin.register(FillBlankExercise)
class FillBlankExerciseAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Fill in the Blank exercises"""
    form = FillBlankExerciseAdminForm
    
    list_display = ('id', 'get_content_lesson', 'get_example_sentence', 'get_available_languages', 
                   'difficulty', 'order', 'created_at')
    list_filter = ('difficulty', 'content_lesson__lesson__unit', 'content_lesson__lesson__unit__level', 'created_at')
    search_fields = ('id', 'content_lesson__title_en', 'content_lesson__lesson__title_en', 'sentences')
    ordering = ('content_lesson', 'order')
    readonly_fields = ('created_at', 'updated_at', 'json_preview', 'lang_consistency_check', 
                       'live_preview', 'answer_validation')
    save_on_top = True
    actions = ['duplicate_exercises', 'export_as_csv', 'export_as_json']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('content_lesson', 'order', 'difficulty')
        }),
        ('Multilingual Content', {
            'fields': ('instructions', 'sentences', 'answer_options', 'correct_answers'),
            'description': 'Set up content in multiple languages (EN, FR, ES, NL, etc.)'
        }),
        ('Learning Aids', {
            'fields': ('hints', 'explanations'),
            'description': 'Optional - Help the user understand the exercise',
            'classes': ('collapse',),
        }),
        ('Live Preview', {
            'fields': ('live_preview',),
            'description': 'See how this exercise will appear to users',
        }),
        ('Validation', {
            'fields': ('answer_validation', 'lang_consistency_check'),
            'description': 'Verify the correctness of your exercise',
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('tags', 'created_at', 'updated_at', 'json_preview'),
            'description': 'Additional information and raw data',
            'classes': ('collapse',),
        }),
    )
    
    def get_content_lesson(self, obj):
        """Display the lesson title with unit info"""
        try:
            unit = obj.content_lesson.lesson.unit
            return format_html(
                '<span title="Unit: {}">[{}] {}</span>',
                unit.title_en,
                unit.level,
                obj.content_lesson.title_en
            )
        except:
            return obj.content_lesson.title_en if obj.content_lesson else "—"
    get_content_lesson.short_description = 'Lesson'
    get_content_lesson.admin_order_field = 'content_lesson__title_en'
    
    def get_example_sentence(self, obj):
        """Display a preview of the exercise sentence"""
        # Try to get English sentence, fallback to first available language
        languages = obj.get_available_languages()
        sentence = ''
        if 'en' in languages and 'en' in obj.sentences:
            sentence = obj.sentences['en']
        elif languages and languages[0] in obj.sentences:
            sentence = obj.sentences[languages[0]]
        
        if not sentence:
            return '—'
        
        # Replace blank with visual indicator
        formatted = sentence.replace('___', '<span style="color: #e91e63; font-weight: bold;">___</span>')
        return format_html('<span style="font-size: 0.85em;">{}</span>', formatted)
    get_example_sentence.short_description = 'Example'
    
    def get_available_languages(self, obj):
        """Display available languages with colored badges"""
        languages = obj.get_available_languages()
        
        # Mappings for language names and colors
        language_names = {
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'nl': 'Dutch',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
        }
        
        colors = {
            'en': '#2196F3', # Blue
            'fr': '#F44336', # Red
            'es': '#FF9800', # Orange
            'nl': '#9C27B0', # Purple
            'de': '#4CAF50', # Green
            'it': '#795548', # Brown
            'pt': '#009688', # Teal
        }
        
        html = []
        for lang in languages:
            color = colors.get(lang, '#607D8B')  # Gray as default
            name = language_names.get(lang, lang.upper())
            html.append(
                f'<span style="background-color: {color}; color: white; padding: 2px 6px; '
                f'border-radius: 3px; margin: 0 2px; font-size: 0.85em;">{name}</span>'
            )
        
        return format_html(' '.join(html) if html else '<span style="color: #999;">None</span>')
    get_available_languages.short_description = 'Languages'
    
    def json_preview(self, obj):
        """Display a formatted JSON preview of the exercise data"""
        sample_data = {
            'instructions': obj.instructions,
            'sentences': obj.sentences,
            'answer_options': obj.answer_options,
            'correct_answers': obj.correct_answers,
        }
        
        formatted_json = json.dumps(sample_data, indent=2, ensure_ascii=False)
        
        return format_html(
            '<div style="font-family: monospace; white-space: pre; '
            'background-color: #f5f5f5; padding: 10px; border-radius: 4px; '
            'max-height: 400px; overflow-y: auto;">{}</div>',
            formatted_json
        )
    json_preview.short_description = 'JSON Data'
    
    def lang_consistency_check(self, obj):
        """Check consistency between languages in different fields"""
        sentence_langs = set(obj.sentences.keys() if obj.sentences else [])
        answer_langs = set(obj.correct_answers.keys() if obj.correct_answers else [])
        options_langs = set(obj.answer_options.keys() if obj.answer_options else [])
        instruction_langs = set(obj.instructions.keys() if obj.instructions else [])
        
        all_langs = sentence_langs.union(answer_langs).union(options_langs).union(instruction_langs)
        
        # Create HTML table for verification
        html = ['<table class="lang-consistency-table" style="width: 100%; border-collapse: collapse;">']
        
        # Table header
        html.append('<thead><tr style="background-color: #263238; color: white;">')
        html.append('<th style="padding: 8px; text-align: left;">Language</th>')
        html.append('<th style="padding: 8px; text-align: center;">Instructions</th>')
        html.append('<th style="padding: 8px; text-align: center;">Sentence</th>')
        html.append('<th style="padding: 8px; text-align: center;">Options</th>')
        html.append('<th style="padding: 8px; text-align: center;">Answer</th>')
        html.append('<th style="padding: 8px; text-align: center;">Status</th>')
        html.append('</tr></thead><tbody>')
        
        # Table body
        for lang in sorted(all_langs):
            has_instruction = lang in instruction_langs
            has_sentence = lang in sentence_langs
            has_options = lang in options_langs
            has_answer = lang in answer_langs
            
            is_complete = has_instruction and has_sentence and has_options and has_answer
            status_label = 'Complete' if is_complete else 'Incomplete'
            bg_color = '#e8f5e9' if is_complete else '#ffebee'
            
            html.append(f'<tr style="background-color: {bg_color};">')
            html.append(f'<td style="padding: 8px; font-weight: bold;">{lang.upper()}</td>')
            
            for has_item in [has_instruction, has_sentence, has_options, has_answer]:
                icon = "✓" if has_item else "✗"
                color = "#4CAF50" if has_item else "#F44336"
                html.append(f'<td style="padding: 8px; text-align: center; color: {color}; font-weight: bold;">{icon}</td>')
            
            status_color = '#2E7D32' if is_complete else '#C62828'
            html.append(f'<td style="padding: 8px; text-align: center; font-weight: bold; color: {status_color};">{status_label}</td>')
            html.append('</tr>')
        
        html.append('</tbody></table>')
        
        # Summary section
        complete_langs = sum(1 for lang in all_langs if lang in sentence_langs and lang in options_langs 
                           and lang in answer_langs and lang in instruction_langs)
        
        html.append('<div style="margin-top: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 4px;">')
        html.append(f'<p style="margin: 5px 0;"><strong>{complete_langs}</strong> complete languages out of <strong>{len(all_langs)}</strong> languages detected.</p>')
        
        if complete_langs < len(all_langs):
            html.append('<p style="margin: 5px 0; color: #C62828;"><strong>⚠️ Warning:</strong> Some languages are incomplete.</p>')
            
            # Add specific recommendations
            for lang in all_langs:
                missing = []
                if lang not in instruction_langs: missing.append("instructions")
                if lang not in sentence_langs: missing.append("sentence")
                if lang not in options_langs: missing.append("options")
                if lang not in answer_langs: missing.append("correct answer")
                
                if missing:
                    html.append(f'<p style="margin: 3px 0; color: #555;">Language <strong>{lang.upper()}</strong> is missing: {", ".join(missing)}</p>')
        
        html.append('</div>')
        
        # Add quick fix buttons
        if complete_langs < len(all_langs):
            html.append('<div style="margin-top: 10px;">')
            html.append('<p><strong>Quick Actions:</strong></p>')
            html.append('<div style="display: flex; gap: 5px; flex-wrap: wrap;">')
            
            for lang in all_langs:
                if lang in sentence_langs and lang in options_langs and lang in answer_langs and lang in instruction_langs:
                    continue  # Skip complete languages
                    
                html.append(f'<button type="button" class="button" onclick="completeLanguage(\'{lang}\')" '
                           f'style="background-color: #2196F3; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer;">'
                           f'Complete {lang.upper()}</button>')
            
            html.append('</div>')
            html.append('</div>')
            
            # Add simple JavaScript for the demo
            html.append('''
            <script>
            function completeLanguage(lang) {
                alert("This would complete the missing fields for language: " + lang.toUpperCase() + 
                      "\\n\\nIn a real implementation, this would copy from other languages or generate placeholders.");
            }
            </script>
            ''')
        
        return format_html(''.join(html))
    lang_consistency_check.short_description = 'Language Consistency'
    
    def live_preview(self, obj):
        """Create an interactive preview of how the exercise will look"""
        languages = obj.get_available_languages()
        if not languages:
            return format_html('<div style="padding: 20px; text-align: center; color: #666; background-color: #f5f5f5; border-radius: 4px;">'
                              'No language content available to preview</div>')
        
        # Create tabs for each language
        html = ['<div class="exercise-preview">']
        
        # Language selector tabs
        html.append('<div class="language-tabs" style="display: flex; gap: 5px; margin-bottom: 10px;">')
        for i, lang in enumerate(languages):
            active = 'active' if i == 0 else ''
            html.append(f'<button type="button" class="lang-tab {active}" data-lang="{lang}" '
                       f'style="background-color: {active and "#2196F3" or "#e0e0e0"}; color: {active and "white" or "#333"}; '
                       f'border: none; padding: 8px 12px; border-radius: 4px 4px 0 0; cursor: pointer;">'
                       f'{lang.upper()}</button>')
        html.append('</div>')
        
        # Exercise content for each language
        html.append('<div class="preview-content" style="border: 1px solid #ddd; border-radius: 0 4px 4px 4px; padding: 20px; background-color: white;">')
        for i, lang in enumerate(languages):
            display = 'block' if i == 0 else 'none'
            
            sentence = obj.sentences.get(lang, '')
            options = obj.answer_options.get(lang, [])
            instruction = obj.instructions.get(lang, 'Select the correct answer')
            correct = obj.correct_answers.get(lang, '')
            
            # Format sentence with blank
            parts = sentence.split('___')
            formatted_sentence = (parts[0] + 
                                 '<span class="blank" style="border-bottom: 2px dashed #2196F3; padding: 0 5px; color: transparent;">___</span>' + 
                                 parts[1]) if len(parts) > 1 else sentence
            
            html.append(f'<div class="lang-content" data-lang="{lang}" style="display: {display};">')
            html.append(f'<h3 style="margin-top: 0; color: #333;">{instruction}</h3>')
            html.append(f'<p class="sentence" style="font-size: 18px; margin: 20px 0;">{formatted_sentence}</p>')
            
            # Options
            html.append('<div class="options" style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px;">')
            for option in options:
                is_correct = option == correct
                data_attr = f'data-correct="{is_correct}"'
                html.append(f'<button type="button" class="option-btn" {data_attr} '
                           f'style="background-color: #f5f5f5; border: 1px solid #ddd; padding: 8px 12px; '
                           f'border-radius: 4px; cursor: pointer; font-size: 16px;">{option}</button>')
            html.append('</div>')
            
            # Feedback area (initially hidden)
            html.append('<div class="feedback" style="margin-top: 20px; padding: 12px; border-radius: 4px; display: none;"></div>')
            
            html.append('</div>')
        html.append('</div>')
        
        # Add JavaScript for interactivity
        html.append('''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Switch tabs
            document.querySelectorAll('.lang-tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    const lang = this.dataset.lang;
                    
                    // Update tab styling
                    document.querySelectorAll('.lang-tab').forEach(t => {
                        t.style.backgroundColor = '#e0e0e0';
                        t.style.color = '#333';
                        t.classList.remove('active');
                    });
                    this.style.backgroundColor = '#2196F3';
                    this.style.color = 'white';
                    this.classList.add('active');
                    
                    // Show selected content
                    document.querySelectorAll('.lang-content').forEach(content => {
                        content.style.display = content.dataset.lang === lang ? 'block' : 'none';
                    });
                });
            });
            
            // Handle option selection
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const isCorrect = this.dataset.correct === 'true';
                    const content = this.closest('.lang-content');
                    const feedback = content.querySelector('.feedback');
                    const sentence = content.querySelector('.sentence');
                    const blank = sentence.querySelector('.blank');
                    
                    // Update blank with the selected option
                    blank.textContent = this.textContent;
                    blank.style.color = 'inherit';
                    blank.style.borderBottom = 'none';
                    blank.style.backgroundColor = isCorrect ? '#E8F5E9' : '#FFEBEE';
                    
                    // Disable all buttons
                    content.querySelectorAll('.option-btn').forEach(b => {
                        b.style.opacity = '0.5';
                        b.style.cursor = 'default';
                        b.disabled = true;
                    });
                    
                    // Highlight the clicked button
                    this.style.opacity = '1';
                    this.style.backgroundColor = isCorrect ? '#4CAF50' : '#F44336';
                    this.style.color = 'white';
                    
                    // Show feedback
                    feedback.style.display = 'block';
                    feedback.style.backgroundColor = isCorrect ? '#E8F5E9' : '#FFEBEE';
                    feedback.style.color = isCorrect ? '#2E7D32' : '#C62828';
                    feedback.innerHTML = isCorrect ? 
                        '<strong>Correct!</strong> Well done.' : 
                        '<strong>Incorrect.</strong> Try again.';
                });
            });
        });
        </script>
        ''')
        
        html.append('</div>')
        
        return format_html(''.join(html))
    live_preview.short_description = 'Exercise Preview'
    
    def answer_validation(self, obj):
        """Validate that correct answers are in the options and other checks"""
        languages = obj.get_available_languages()
        if not languages:
            return format_html('<div style="padding: 10px; color: #666;">No content to validate</div>')
        
        issues = []
        
        # Check for each language
        for lang in languages:
            sentence = obj.sentences.get(lang, '')
            options = obj.answer_options.get(lang, [])
            correct = obj.correct_answers.get(lang, '')
            
            # Check if sentence has a blank
            if '___' not in sentence:
                issues.append((
                    'error', 
                    f'The sentence for language <strong>{lang.upper()}</strong> does not contain a blank marker (___)'
                ))
            
            # Check if correct answer is in options
            if options and correct and correct not in options:
                issues.append((
                    'error',
                    f'The correct answer <strong>"{correct}"</strong> for language <strong>{lang.upper()}</strong> is not in the options list'
                ))
            
            # Check if options contain duplicates
            if options and len(options) != len(set(options)):
                issues.append((
                    'warning',
                    f'The options for language <strong>{lang.upper()}</strong> contain duplicate values'
                ))
            
            # Check if blank is too small for options
            if options:
                max_len = max([len(opt) for opt in options])
                if max_len > 30:  # Arbitrary threshold
                    issues.append((
                        'warning',
                        f'Some answer options for language <strong>{lang.upper()}</strong> are very long ({max_len} chars)'
                    ))
        
        # Build the output HTML
        html = ['<div class="validation-results">']
        
        if not issues:
            html.append('<div style="padding: 10px; background-color: #E8F5E9; color: #2E7D32; border-radius: 4px;">'
                        '<strong>✓ All validation checks passed!</strong> No issues found.'
                        '</div>')
        else:
            html.append('<div style="padding: 10px; background-color: #FFF3E0; color: #E65100; border-radius: 4px;">'
                        f'<strong>⚠️ {len(issues)} issue(s) found</strong>'
                        '</div>')
            
            html.append('<ul style="list-style-type: none; padding-left: 0;">')
            for issue_type, message in issues:
                icon = '❌' if issue_type == 'error' else '⚠️'
                color = '#C62828' if issue_type == 'error' else '#F57F17'
                html.append(f'<li style="margin: 8px 0; padding: 8px; background-color: {issue_type == "error" and "#FFEBEE" or "#FFF8E1"}; '
                           f'border-radius: 4px; color: {color};">{icon} {message}</li>')
            html.append('</ul>')
        
        html.append('</div>')
        
        return format_html(''.join(html))
    answer_validation.short_description = 'Validation Results'
    
    def save_model(self, request, obj, form, change):
        """Validate and clean JSON data before saving"""
        # Ensure instructions field exists for all languages
        if not hasattr(obj, 'instructions') or not obj.instructions:
            obj.instructions = {}
        
        # For each language in sentences, ensure it has instructions
        for lang in obj.sentences.keys():
            if lang not in obj.instructions:
                # Add default instruction based on language
                if lang == 'en':
                    obj.instructions[lang] = "Select the correct answer to fill in the blank."
                elif lang == 'fr':
                    obj.instructions[lang] = "Sélectionnez la bonne réponse pour compléter la phrase."
                elif lang == 'es':
                    obj.instructions[lang] = "Selecciona la respuesta correcta para completar el espacio en blanco."
                elif lang == 'nl':
                    obj.instructions[lang] = "Selecteer het juiste antwoord om de zin aan te vullen."
                else:
                    obj.instructions[lang] = "Select the correct answer."
        
        # Check for inconsistencies between fields
        sentence_langs = set(obj.sentences.keys() if obj.sentences else [])
        answer_langs = set(obj.correct_answers.keys() if obj.correct_answers else [])
        options_langs = set(obj.answer_options.keys() if obj.answer_options else [])
        
        # Identify missing elements
        missing_sentences = answer_langs.difference(sentence_langs)
        missing_answers = sentence_langs.difference(answer_langs)
        missing_options = sentence_langs.difference(options_langs)
        
        # Display warnings for inconsistencies
        warnings = []
        
        if missing_sentences:
            warnings.append(f"Missing sentences for languages: {', '.join(missing_sentences)}")
        
        if missing_answers:
            warnings.append(f"Missing correct answers for languages: {', '.join(missing_answers)}")
            
        if missing_options:
            warnings.append(f"Missing answer options for languages: {', '.join(missing_options)}")
        
        for warning in warnings:
            self.message_user(
                request, 
                f"⚠️ {warning}",
                level=messages.WARNING
            )
        
        super().save_model(request, obj, form, change)
    
    # Custom actions
    def duplicate_exercises(self, request, queryset):
        """Create copies of selected exercises"""
        count = 0
        for exercise in queryset:
            # Create new object
            new_exercise = FillBlankExercise.objects.create(
                content_lesson=exercise.content_lesson,
                order=exercise.order + 1000,  # Temporary high order to avoid collision
                difficulty=exercise.difficulty,
                instructions=exercise.instructions,
                sentences=exercise.sentences,
                answer_options=exercise.answer_options,
                correct_answers=exercise.correct_answers,
                hints=exercise.hints,
                explanations=exercise.explanations,
                tags=exercise.tags
            )
            count += 1
        
        # Reorder exercises
        self._reorder_exercises()
        
        self.message_user(request, f"Successfully duplicated {count} exercise(s).", messages.SUCCESS)
    duplicate_exercises.short_description = "Duplicate selected exercises"
    
    def export_as_csv(self, request, queryset):
        """Export selected exercises as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="exercises.csv"'
        
        writer = csv.writer(response)
        # Write header
        writer.writerow([
            'ID', 'Content Lesson', 'Order', 'Difficulty', 
            'Languages', 'Created', 'Updated'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.content_lesson.title_en if obj.content_lesson else '',
                obj.order,
                obj.difficulty,
                ', '.join(obj.get_available_languages()),
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
                obj.updated_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
    export_as_csv.short_description = "Export selected as CSV"
    
    def export_as_json(self, request, queryset):
        """Export selected exercises as JSON"""
        data = []
        for obj in queryset:
            data.append({
                'id': obj.id,
                'content_lesson_id': obj.content_lesson_id,
                'order': obj.order,
                'difficulty': obj.difficulty,
                'instructions': obj.instructions,
                'sentences': obj.sentences,
                'answer_options': obj.answer_options,
                'correct_answers': obj.correct_answers,
                'hints': obj.hints,
                'explanations': obj.explanations,
                'tags': obj.tags,
                'created_at': obj.created_at.isoformat(),
                'updated_at': obj.updated_at.isoformat()
            })
        
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="exercises.json"'
        return response
    export_as_json.short_description = "Export selected as JSON"
    
    def _reorder_exercises(self):
        """Reorder exercises by content_lesson to ensure consistent ordering"""
        from django.db.models import F, Window
        from django.db.models.functions import RowNumber
        
        # Group by content_lesson and assign new order values
        content_lessons = FillBlankExercise.objects.values_list('content_lesson', flat=True).distinct()
        
        for content_lesson_id in content_lessons:
            exercises = FillBlankExercise.objects.filter(content_lesson_id=content_lesson_id).order_by('order')
            
            # Update order sequentially
            for i, exercise in enumerate(exercises, 1):
                if exercise.order != i:
                    exercise.order = i
                    exercise.save(update_fields=['order'])
    
    # Custom views
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('quick-create/', self.admin_site.admin_view(self.quick_create_view), name='matchingexercise_quick_create'),
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='fillblankexercise_import_csv'),
            path('export-template/', self.admin_site.admin_view(self.export_template_view), name='fillblankexercise_export_template'),
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='fillblankexercise_bulk_create'),
            path('preview/<int:pk>/', self.admin_site.admin_view(self.preview_view), name='fillblankexercise_preview'),
        ]
        return custom_urls + urls
        
    def quick_create_view(self, request):
        """Vue pour créer rapidement un exercice de matching avec tous les éléments"""
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Création rapide d\'exercice de matching',
            'form': None,
        }
        
        if request.method == 'POST':
            form = QuickMatchingExerciseForm(request.POST)
            context['form'] = form
            
            if form.is_valid():
                try:
                    with transaction.atomic():
                        lesson = form.cleaned_data['lesson']
                        
                        # 1. Créer le ContentLesson
                        content_lesson = ContentLesson.objects.create(
                            lesson=lesson,
                            content_type=form.cleaned_data['content_type'],
                            title_en=form.cleaned_data['title_en'],
                            title_fr=form.cleaned_data['title_fr'],
                            title_es=form.cleaned_data['title_es'],
                            title_nl=form.cleaned_data['title_nl'],
                            instruction_en=form.cleaned_data['instruction_en'],
                            instruction_fr=form.cleaned_data['instruction_fr'],
                            instruction_es=form.cleaned_data['instruction_es'],
                            instruction_nl=form.cleaned_data['instruction_nl'],
                            estimated_duration=form.cleaned_data['estimated_duration'],
                            order=ContentLesson.objects.filter(lesson=lesson).count() + 1
                        )
                        
                        # 2. Créer le MatchingExercise
                        exercise = MatchingExercise.objects.create(
                            content_lesson=content_lesson,
                            difficulty=form.cleaned_data['difficulty'],
                            title_en=form.cleaned_data['title_en'],
                            title_fr=form.cleaned_data['title_fr'],
                            title_es=form.cleaned_data['title_es'],
                            title_nl=form.cleaned_data['title_nl'],
                            pairs_count=form.cleaned_data['pairs_count'],
                            order=1  # Premier exercice pour ce ContentLesson
                        )
                        
                        # 3. Associer automatiquement le vocabulaire si demandé
                        if form.cleaned_data['use_vocabulary']:
                            # Trouver le vocabulaire disponible
                            vocabulary_items = VocabularyList.objects.filter(
                                content_lesson__lesson=lesson
                            )[:form.cleaned_data['pairs_count']]
                            
                            if vocabulary_items.exists():
                                # Ajouter le vocabulaire trouvé à l'exercice
                                for vocab in vocabulary_items:
                                    exercise.vocabulary_words.add(vocab)
                    
                    # Afficher un message de succès
                    messages.success(
                        request,
                        f"L'exercice '{form.cleaned_data['title_en']}' a été créé avec succès."
                    )
                    
                    # Rediriger vers la page d'édition du MatchingExercise
                    return redirect('admin:course_matchingexercise_change', exercise.id)
                    
                except Exception as e:
                    messages.error(request, f"Erreur lors de la création: {str(e)}")
        else:
            form = QuickMatchingExerciseForm()
            context['form'] = form
            
            # Ajouter une liste des leçons qui contiennent du vocabulaire
            lessons_with_vocab = Lesson.objects.filter(
                content_lessons__vocabulary_lists__isnull=False
            ).distinct().order_by('unit__level', 'unit__order', 'order')
            
            context['lessons_with_vocab'] = lessons_with_vocab
            context['vocab_counts'] = {
                lesson.id: VocabularyList.objects.filter(
                    content_lesson__lesson=lesson
                ).count() for lesson in lessons_with_vocab
            }
        
        return TemplateResponse(request, 'admin/course/matchingexercise/quick_create.html', context)
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """Improved view for importing exercises from CSV"""
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Import Fill in the Blank Exercises',
            'content_lessons': ContentLesson.objects.select_related('lesson__unit').order_by(
                'lesson__unit__level', 'lesson__unit__order', 'lesson__order', 'order'
            ),
        }
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            content_lesson_id = request.POST.get('content_lesson')
            
            if not csv_file:
                messages.error(request, "No CSV file selected")
                return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
            
            if not content_lesson_id:
                messages.error(request, "No content lesson selected")
                return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
            
            try:
                content_lesson = ContentLesson.objects.get(id=content_lesson_id)
                
                # Parse CSV file
                csv_data = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(csv_data))
                
                # Process each row
                exercises_created = []
                errors = []
                
                for i, row in enumerate(reader, start=1):
                    try:
                        # Extract languages from headers
                        languages = self._extract_languages_from_headers(reader.fieldnames)
                        
                        # Basic validation
                        if not self._validate_csv_row(row, languages):
                            errors.append(f"Row {i}: Incomplete or invalid data")
                            continue
                        
                        # Prepare data structures
                        sentences = {}
                        options = {}
                        answers = {}
                        hints = {}
                        explanations = {}
                        
                        # Populate data for each language
                        for lang in languages:
                            # Required fields
                            sentence_key = f'sentence_{lang}'
                            options_key = f'options_{lang}'
                            answer_key = f'answer_{lang}'
                            
                            if sentence_key in row and row[sentence_key]:
                                sentences[lang] = row[sentence_key]
                            
                            if options_key in row and row[options_key]:
                                # Convert comma-separated options to list
                                options[lang] = [opt.strip() for opt in row[options_key].split(',')]
                            
                            if answer_key in row and row[answer_key]:
                                answers[lang] = row[answer_key]
                            
                            # Optional fields
                            hint_key = f'hint_{lang}'
                            explanation_key = f'explanation_{lang}'
                            
                            if hint_key in row and row[hint_key]:
                                hints[lang] = row[hint_key]
                            
                            if explanation_key in row and row[explanation_key]:
                                explanations[lang] = row[explanation_key]
                        
                        # Get metadata
                        order = int(row.get('order', 1))
                        difficulty = row.get('difficulty', 'medium')
                        tags = row.get('tags', '').split(',') if row.get('tags') else []
                        
                        # Create default instructions if not provided
                        instructions = {}
                        for lang in languages:
                            if lang == 'en':
                                instructions[lang] = "Select the correct answer to fill in the blank."
                            elif lang == 'fr':
                                instructions[lang] = "Sélectionnez la bonne réponse pour compléter la phrase."
                            elif lang == 'es':
                                instructions[lang] = "Selecciona la respuesta correcta para completar el espacio en blanco."
                            elif lang == 'nl':
                                instructions[lang] = "Selecteer het juiste antwoord om de zin aan te vullen."
                            else:
                                instructions[lang] = "Select the correct answer."
                        
                        # Create or update exercise
                        exercise, created = FillBlankExercise.objects.update_or_create(
                            content_lesson=content_lesson,
                            order=order,
                            defaults={
                                'sentences': sentences,
                                'answer_options': options,
                                'correct_answers': answers,
                                'difficulty': difficulty,
                                'hints': hints or None,
                                'explanations': explanations or None,
                                'instructions': instructions,
                                'tags': tags
                            }
                        )
                        
                        exercises_created.append(exercise)
                    except Exception as e:
                        errors.append(f"Row {i}: {str(e)}")
                
                # Show results
                if exercises_created:
                    messages.success(
                        request, 
                        f"Successfully imported {len(exercises_created)} exercises for lesson '{content_lesson.title_en}'"
                    )
                
                if errors:
                    messages.warning(
                        request, 
                        f"{len(errors)} errors during import: {', '.join(errors[:5])}" +
                        (f"... and {len(errors) - 5} more" if len(errors) > 5 else "")
                    )
                
                # Redirect to list view
                return redirect('admin:course_fillblankexercise_changelist')
                
            except Exception as e:
                messages.error(request, f"Error during import: {str(e)}")
        
        # Add sample CSV data to context
        context['sample_csv'] = self._get_sample_csv()
        
        return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
    
    def export_template_view(self, request):
        """Export a CSV template for importing exercises"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fill_blank_template.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'order', 'difficulty', 'tags',
            'sentence_en', 'options_en', 'answer_en', 'hint_en', 'explanation_en',
            'sentence_fr', 'options_fr', 'answer_fr', 'hint_fr', 'explanation_fr',
            'sentence_es', 'options_es', 'answer_es', 'hint_es', 'explanation_es',
            'sentence_nl', 'options_nl', 'answer_nl', 'hint_nl', 'explanation_nl'
        ])
        
        # Add sample row
        writer.writerow([
            '1', 'medium', 'grammar,article,beginner',
            'Paris is ___ in France.', 'located,situated,found,placed', 'located', 'Think about position', 'We use "located" to describe the position of a place',
            'Paris est ___ en France.', 'situé,localisé,placé,trouvé', 'situé', 'Pensez à la position', 'Nous utilisons "situé" pour décrire la position d\'un lieu',
            'París está ___ en Francia.', 'ubicado,situado,localizado,encontrado', 'ubicado', 'Piensa en la posición', 'Usamos "ubicado" para describir la posición de un lugar',
            'Parijs is ___ in Frankrijk.', 'gelegen,gesitueerd,geplaatst,gevonden', 'gelegen', 'Denk aan positie', 'We gebruiken "gelegen" om de positie van een plaats te beschrijven'
        ])
        
        return response
    
    def bulk_create_view(self, request):
        """View for creating multiple exercises at once"""
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Bulk Create Fill in the Blank Exercises',
            'content_lessons': ContentLesson.objects.select_related('lesson__unit').order_by(
                'lesson__unit__level', 'lesson__unit__order', 'lesson__order', 'order'
            ),
        }
        
        if request.method == 'POST':
            content_lesson_id = request.POST.get('content_lesson')
            bulk_data = request.POST.get('bulk_data', '')
            
            if not content_lesson_id:
                messages.error(request, "No content lesson selected")
                return TemplateResponse(request, "admin/fillblankexercise/bulk_create.html", context)
            
            if not bulk_data.strip():
                messages.error(request, "No data provided")
                return TemplateResponse(request, "admin/fillblankexercise/bulk_create.html", context)
            
            try:
                content_lesson = ContentLesson.objects.get(id=content_lesson_id)
                
                # Process bulk data (one exercise per paragraph)
                exercises_created = []
                errors = []
                
                # Split into paragraphs
                paragraphs = [p.strip() for p in bulk_data.split('\n\n') if p.strip()]
                
                for i, paragraph in enumerate(paragraphs, 1):
                    try:
                        lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
                        
                        if len(lines) < 3:  # Need at least sentence, options and answer
                            errors.append(f"Paragraph {i}: Not enough data (need at least sentence, options, answer)")
                            continue
                        
                        # Parse data (simple format)
                        sentence = lines[0]
                        options = [opt.strip() for opt in lines[1].split(',')]
                        answer = lines[2]
                        
                        # Optional hint and explanation
                        hint = lines[3] if len(lines) > 3 else None
                        explanation = lines[4] if len(lines) > 4 else None
                        
                        # Create exercise (English only in this simple implementation)
                        # In a real implementation, you'd handle multiple languages
                        exercise = FillBlankExercise.objects.create(
                            content_lesson=content_lesson,
                            order=i,
                            difficulty='medium',
                            instructions={'en': 'Select the correct answer to fill in the blank.'},
                            sentences={'en': sentence},
                            answer_options={'en': options},
                            correct_answers={'en': answer}
                        )
                        
                        if hint:
                            exercise.hints = {'en': hint}
                            
                        if explanation:
                            exercise.explanations = {'en': explanation}
                            
                        exercise.save()
                        exercises_created.append(exercise)
                        
                    except Exception as e:
                        errors.append(f"Paragraph {i}: {str(e)}")
                
                # Show results
                if exercises_created:
                    messages.success(
                        request, 
                        f"Successfully created {len(exercises_created)} exercises for lesson '{content_lesson.title_en}'"
                    )
                
                if errors:
                    messages.warning(
                        request, 
                        f"{len(errors)} errors during creation: {', '.join(errors[:5])}" +
                        (f"... and {len(errors) - 5} more" if len(errors) > 5 else "")
                    )
                
                # Redirect to list view
                return redirect('admin:course_fillblankexercise_changelist')
                
            except Exception as e:
                messages.error(request, f"Error creating exercises: {str(e)}")
        
        # Add sample bulk data to context
        context['sample_data'] = "Paris is ___ in France.\nlocated,situated,found,placed\nlocated\nThink about position\nWe use 'located' to describe the position of a place\n\nThe weather ___ very nice today.\nis,are,were,have been\nis\nConsider singular/plural\n'Weather' is a singular noun so we use 'is'"
        
        return TemplateResponse(request, "admin/fillblankexercise/bulk_create.html", context)
    
    def preview_view(self, request, pk):
        """Standalone preview view for an exercise"""
        try:
            exercise = FillBlankExercise.objects.get(pk=pk)
        except FillBlankExercise.DoesNotExist:
            messages.error(request, "Exercise not found")
            return redirect('admin:course_fillblankexercise_changelist')
        
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': f'Preview Exercise #{pk}',
            'exercise': exercise,
            'languages': exercise.get_available_languages(),
        }
        
        return TemplateResponse(request, "admin/fillblankexercise/preview.html", context)
    
    def _extract_languages_from_headers(self, headers):
        """Extract language codes from CSV headers"""
        languages = set()
        
        for header in headers:
            if header.startswith(('sentence_', 'options_', 'answer_')):
                parts = header.split('_')
                if len(parts) >= 2:
                    lang = parts[1]
                    languages.add(lang)
        
        return languages
    
    def _validate_csv_row(self, row, languages):
        """Validate CSV row has required data for at least one language"""
        for lang in languages:
            sentence_key = f'sentence_{lang}'
            options_key = f'options_{lang}'
            answer_key = f'answer_{lang}'
            
            if (sentence_key in row and row[sentence_key] and
                options_key in row and row[options_key] and
                answer_key in row and row[answer_key]):
                return True
        
        return False
    
    def _get_sample_csv(self):
        """Generate sample CSV data"""
        return (
            "order,difficulty,tags,sentence_en,options_en,answer_en,hint_en,explanation_en\n"
            "1,easy,grammar,She ___ to school every day.,goes,walks,runs,drives,goes,Think about regular actions,We use 'goes' for regular actions\n"
            "2,medium,prepositions,The book is ___ the table.,on,in,at,under,on,Think about position,We use 'on' when something is supported by a surface"
        )
    
    # Add the export template button to the change list
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_export_template_button'] = True
        extra_context['show_bulk_create_button'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            'all': ('css/json_prettify.css',)
        }
        js = ('js/json_prettify.js',)





"""
Admin interfaces for Test Recap functionality in the Linguify course app.
Will be merged into the main admin.py file after review.
"""
class TestRecapQuestionInline(admin.TabularInline):
    """Inline editor for test recap questions."""
    model = TestRecapQuestion
    extra = 0
    fields = ('question_type', 'order', 'points', 'content_id_field', 'get_question_preview')
    readonly_fields = ('get_question_preview', 'content_id_field')
    
    
    def get_question_preview(self, obj):
        """Show a preview of the question based on its type."""
        if not obj.pk:
            return "-"
            
        question = obj.get_question_content()
        if not question:
            return format_html('<span style="color:red">Missing content</span>')
        
        if obj.question_type == 'multiple_choice':
            return format_html('<strong>Q:</strong> {} <br/><strong>A:</strong> {}', 
                               question.question_en[:50], 
                               question.correct_answer_en)
        
        elif obj.question_type == 'fill_blank':
            return format_html('<strong>Sentence:</strong> {}', 
                               question.sentences.get('en', '')[:50])
        
        elif obj.question_type == 'matching':
            return format_html('<strong>Matching:</strong> {} pairs', 
                               question.vocabulary_words.count())
        
        elif obj.question_type == 'reordering':
            return format_html('<strong>Sentence:</strong> {}', 
                               question.sentence_en[:50])
        
        elif obj.question_type == 'speaking':
            vocab_count = question.vocabulary_items.count()
            return format_html('<strong>Speaking:</strong> {} vocabulary items', 
                               vocab_count)
        
        elif obj.question_type == 'vocabulary':
            return format_html('<strong>Word:</strong> {} - {}', 
                               question.word_en,
                               question.definition_en[:30])
        
        return "Unknown question type"
    
    get_question_preview.short_description = 'Preview'
    
    def content_id_field(self, obj):
        """Display the appropriate content ID field based on question type."""
        if not obj or not obj.pk:
            return "-"
            
        field_map = {
            'multiple_choice': obj.multiple_choice_id,
            'fill_blank': obj.fill_blank_id,
            'matching': obj.matching_id,
            'reordering': obj.reordering_id,
            'speaking': obj.speaking_id,
            'vocabulary': obj.vocabulary_id,
        }
        
        return field_map.get(obj.question_type, "-")
    
    content_id_field.short_description = 'Content ID'


@admin.register(TestRecap)
class TestRecapAdmin(admin.ModelAdmin):
    """Admin interface for test recap management."""
    list_display = ('id', 'get_title', 'get_lesson', 'passing_score', 'time_limit', 
                    'is_active', 'questions_count', 'created_at', 'has_content_lesson')
    list_filter = ('is_active', 'lesson__unit__level', 'lesson__unit')
    search_fields = ('title', 'title_en', 'title_fr', 'lesson__title_en')
    inlines = [TestRecapQuestionInline]
    actions = ['generate_test_questions', 'duplicate_test', 'ensure_content_lessons']
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure content lesson exists."""
        super().save_model(request, obj, form, change)
        
        # Don't proceed if no lesson assigned
        if not obj.lesson:
            return
            
        # Check if content lesson already exists
        content_lesson = ContentLesson.objects.filter(
            lesson=obj.lesson,
            content_type='test_recap'
        ).first()
        
        # Create one if it doesn't exist
        if not content_lesson:
            ContentLesson.objects.create(
                lesson=obj.lesson,
                content_type='test_recap',
                title_en=f"Test Recap: {obj.lesson.title_en}",
                title_fr=f"Test Récapitulatif: {obj.lesson.title_fr}",
                title_es=f"Test de Repaso: {obj.lesson.title_es}",
                title_nl=f"Test Overzicht: {obj.lesson.title_nl}",
                instruction_en="This test covers all topics from this lesson. Complete all sections to review your understanding.",
                instruction_fr="Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.",
                instruction_es="Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.",
                instruction_nl="Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.",
                estimated_duration=30,
                order=99  # High order so it appears at the end
            )
            
            # Add a message to inform the admin
            messages.success(request, "A Content Lesson of type 'test_recap' was automatically created.")
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'is_active', 'passing_score', 'time_limit')
        }),
        ('Titles', {
            'fields': ('title', 'title_en', 'title_fr', 'title_es', 'title_nl')
        }),
        ('Legacy Fields', {
            'fields': ('question',),
            'classes': ('collapse',),
        }),
        ('Descriptions', {
            'fields': ('description_en', 'description_fr', 'description_es', 'description_nl')
        }),
    )
    
    def get_title(self, obj):
        """Display title in multiple languages."""
        return format_html(
            "<strong>{}</strong><br/>"
            "<small style='color:#666'>{} | {} | {}</small>",
            obj.title_en, 
            obj.title_fr, 
            obj.title_es, 
            obj.title_nl
        )
    
    get_title.short_description = 'Title'
    
    def get_lesson(self, obj):
        """Display lesson with its unit and level."""
        if not obj.lesson or not obj.lesson.unit:
            return "-"
        
        return format_html(
            "[{}] {} <br/><small>Unit: {}</small>",
            obj.lesson.unit.level,
            obj.lesson.title_en,
            obj.lesson.unit.title_en
        )
    
    get_lesson.short_description = 'Lesson'
    
    def questions_count(self, obj):
        """Display number of questions with visual indicator."""
        count = obj.questions.count()
        if count == 0:
            color = 'red'
        elif count < 5:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color:white; background-color:{0}; padding:3px 8px; '
            'border-radius:10px; font-weight:bold">{1}</span>',
            color, count
        )
    
    questions_count.short_description = 'Questions'
    
    def generate_test_questions(self, request, queryset):
        """Generate questions for selected test recaps."""
        from .models import generate_test_recap
        
        updated = 0
        for test in queryset:
            # Clear existing questions
            test.questions.all().delete()
            
            # Generate new questions
            generate_test_recap(test.lesson)
            updated += 1
            
        self.message_user(
            request,
            f"Questions generated for {updated} test(s)."
        )
    
    generate_test_questions.short_description = "Generate questions for selected tests"
    
    def has_content_lesson(self, obj):
        """Check if this test recap has a corresponding content lesson."""
        if not obj.lesson:
            return False
            
        content_lesson = ContentLesson.objects.filter(
            lesson=obj.lesson,
            content_type='test_recap'
        ).exists()
        
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if content_lesson else 'red',
            '✓' if content_lesson else '✗'
        )
    
    has_content_lesson.short_description = 'In Content'
    
    def ensure_content_lessons(self, request, queryset):
        """Ensure all selected test recaps have corresponding content lessons."""
        created = 0
        for test in queryset:
            if not test.lesson:
                continue
                
            # Check if content lesson already exists
            content_lesson = ContentLesson.objects.filter(
                lesson=test.lesson,
                content_type='test_recap'
            ).first()
            
            # Create one if it doesn't exist
            if not content_lesson:
                ContentLesson.objects.create(
                    lesson=test.lesson,
                    content_type='test_recap',
                    title_en=f"Test Recap: {test.lesson.title_en}",
                    title_fr=f"Test Récapitulatif: {test.lesson.title_fr}",
                    title_es=f"Test de Repaso: {test.lesson.title_es}",
                    title_nl=f"Test Overzicht: {test.lesson.title_nl}",
                    instruction_en="This test covers all topics from this lesson. Complete all sections to review your understanding.",
                    instruction_fr="Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.",
                    instruction_es="Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.",
                    instruction_nl="Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.",
                    estimated_duration=30,
                    order=99  # High order so it appears at the end
                )
                created += 1
        
        if created:
            self.message_user(
                request,
                f"Created {created} content lesson(s) for test recap(s)."
            )
        else:
            self.message_user(
                request,
                "All selected test recaps already have content lessons."
            )
    
    ensure_content_lessons.short_description = "Create content lessons for selected tests"
    
    def duplicate_test(self, request, queryset):
        """Duplicate selected test recaps."""
        duplicated = 0
        
        for test in queryset:
            with transaction.atomic():
                # Create new test recap
                new_title_en = f"Copy of {test.title_en}"
                new_test = TestRecap.objects.create(
                    lesson=test.lesson,
                    title=new_title_en,  # Set main title field
                    title_en=new_title_en,
                    title_fr=f"Copie de {test.title_fr}",
                    title_es=f"Copia de {test.title_es}",
                    title_nl=f"Kopie van {test.title_nl}",
                    question=new_title_en,  # Legacy field required by the database
                    description_en=test.description_en,
                    description_fr=test.description_fr,
                    description_es=test.description_es,
                    description_nl=test.description_nl,
                    passing_score=test.passing_score,
                    time_limit=test.time_limit,
                    is_active=False  # Default to inactive for safety
                )
                
                # Create ContentLesson of type test_recap for this TestRecap
                content_lesson = ContentLesson.objects.filter(
                    lesson=test.lesson,
                    content_type='test_recap'
                ).first()
                
                # Only create if none exists yet
                if not content_lesson:
                    ContentLesson.objects.create(
                        lesson=test.lesson,
                        content_type='test_recap',
                        title_en=f"Test Recap: {test.lesson.title_en}",
                        title_fr=f"Test Récapitulatif: {test.lesson.title_fr}",
                        title_es=f"Test de Repaso: {test.lesson.title_es}",
                        title_nl=f"Test Overzicht: {test.lesson.title_nl}",
                        instruction_en="This test covers all topics from this lesson. Complete all sections to review your understanding.",
                        instruction_fr="Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.",
                        instruction_es="Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.",
                        instruction_nl="Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.",
                        estimated_duration=30,
                        order=99  # High order so it appears at the end
                    )
                
                # Duplicate questions
                for question in test.questions.all():
                    TestRecapQuestion.objects.create(
                        test_recap=new_test,
                        question_type=question.question_type,
                        multiple_choice_id=question.multiple_choice_id,
                        fill_blank_id=question.fill_blank_id,
                        matching_id=question.matching_id,
                        reordering_id=question.reordering_id,
                        speaking_id=question.speaking_id,
                        vocabulary_id=question.vocabulary_id,
                        order=question.order,
                        points=question.points
                    )
                
                duplicated += 1
        
        self.message_user(
            request,
            f"Successfully duplicated {duplicated} test(s). New tests are inactive by default."
        )
    
    duplicate_test.short_description = "Duplicate selected tests"


@admin.register(TestRecapResult)
class TestRecapResultAdmin(admin.ModelAdmin):
    """Admin interface for test recap results."""
    list_display = ('id', 'get_user', 'get_test', 'score', 'passed', 
                    'time_spent_formatted', 'completed_at')
    list_filter = ('passed', 'test_recap__lesson__unit__level', 
                   'test_recap__lesson__unit', 'completed_at')
    search_fields = ('user__username', 'user__email', 'test_recap__title_en')
    readonly_fields = ('user', 'test_recap', 'score', 'passed', 'time_spent', 
                       'completed_at', 'detailed_results', 'get_detailed_results_table')
    
    fieldsets = (
        ('Result Information', {
            'fields': ('user', 'test_recap', 'score', 'passed', 'time_spent', 'completed_at')
        }),
        ('Detailed Results', {
            'fields': ('get_detailed_results_table',),
            'classes': ('collapse',),
        }),
    )
    
    def get_user(self, obj):
        """Display user with email."""
        return format_html(
            "{}<br/><small>{}</small>",
            obj.user.username,
            obj.user.email
        )
    
    get_user.short_description = 'User'
    
    def get_test(self, obj):
        """Display test recap with lesson."""
        return format_html(
            "{}<br/><small>Lesson: {}</small>",
            obj.test_recap.title_en,
            obj.test_recap.lesson.title_en if obj.test_recap.lesson else "N/A"
        )
    
    get_test.short_description = 'Test'
    
    def time_spent_formatted(self, obj):
        """Format time spent in minutes and seconds."""
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}m {seconds}s"
    
    time_spent_formatted.short_description = 'Time Spent'
    
    def get_detailed_results_table(self, obj):
        """Format detailed results as an HTML table."""
        if not obj.detailed_results:
            return "No detailed results available"
        
        html = ["<table style='width:100%; border-collapse:collapse;'>",
                "<tr><th style='border:1px solid #ddd; padding:8px;'>Question</th>",
                "<th style='border:1px solid #ddd; padding:8px;'>Correct</th>",
                "<th style='border:1px solid #ddd; padding:8px;'>Time Spent</th>",
                "<th style='border:1px solid #ddd; padding:8px;'>User Answer</th></tr>"]
        
        for question_id, result in obj.detailed_results.items():
            question = TestRecapQuestion.objects.filter(id=question_id).first()
            question_text = f"Q{question.order}" if question else question_id
            
            is_correct = result.get('correct', False)
            color = "green" if is_correct else "red"
            correct_text = "✓" if is_correct else "✗"
            
            time_spent = result.get('time_spent', 0)
            time_text = f"{time_spent}s"
            
            answer = result.get('answer', 'N/A')
            
            html.append(f"<tr>")
            html.append(f"<td style='border:1px solid #ddd; padding:8px;'>{question_text}</td>")
            html.append(f"<td style='border:1px solid #ddd; padding:8px; color:{color};'>{correct_text}</td>")
            html.append(f"<td style='border:1px solid #ddd; padding:8px;'>{time_text}</td>")
            html.append(f"<td style='border:1px solid #ddd; padding:8px;'>{answer}</td>")
            html.append(f"</tr>")
        
        html.append("</table>")
        return format_html("".join(html))
    
    get_detailed_results_table.short_description = 'Detailed Results'