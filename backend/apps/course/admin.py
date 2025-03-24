# course/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .widgets import AdminJSONFormField
from .models import (
    Unit, 
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    ExerciseVocabularyMultipleChoice, 
    MultipleChoiceQuestion, 
    Numbers,
    ExerciseGrammarReordering,
    FillBlankExercise,
)
import csv, io, json
from django.contrib import messages
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect

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

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_title', 'unit', 'lesson_type', 'estimated_duration', 'order', 'content_count')
    list_filter = ('lesson_type', 'unit')
    search_fields = ('title_en', 'title_fr', 'description_en')
    ordering = ('unit', 'order')
    inlines = [ContentLessonInline]
    
    def get_title(self, obj):
        return f"{obj.title_en} | {obj.title_fr}"
    get_title.short_description = 'Title'
    
    def content_count(self, obj):
        count = obj.content_lessons.count()
        return format_html('<span style="color: {};">{}</span>', 
                          'green' if count > 0 else 'red', 
                          f"{count} contents")
    content_count.short_description = 'Contents'

@admin.register(ContentLesson)
class ContentLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_title', 'content_type', 'lesson', 'order')
    list_filter = ('content_type', 'lesson__unit')
    search_fields = ('title_en', 'title_fr', 'instruction_en')
    ordering = ('lesson', 'order')
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'content_type', 'order', 'estimated_duration')
        }),
        ('English Content', {
            'fields': ('title_en', 'instruction_en'),
        }),
        ('French Content', {
            'fields': ('title_fr', 'instruction_fr'),
        }),
        ('Spanish Content', {
            'fields': ('title_es', 'instruction_es'),
        }),
        ('Dutch Content', {
            'fields': ('title_nl', 'instruction_nl'),
        }),
    )
    
    def get_title(self, obj):
        return f"{obj.title_en} | {obj.title_fr}"
    get_title.short_description = 'Title'

@admin.register(TheoryContent)
class TheoryContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_content_title', 'has_formula', 'has_examples')
    list_filter = ('content_lesson__lesson__unit',)
    search_fields = ('content_en', 'content_fr', 'content_lesson__title_en')
    fieldsets = (
        ('Lesson Reference', {
            'fields': ('content_lesson',)
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
    )
    
    def get_content_title(self, obj):
        return obj.content_lesson.title_en
    get_content_title.short_description = 'Content Title'
    
    def has_formula(self, obj):
        return bool(obj.formula_en)
    has_formula.boolean = True
    
    def has_examples(self, obj):
        return bool(obj.example_en)
    has_examples.boolean = True

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
    """Formulaire personnalisé pour l'admin des exercices à trous"""
    
    instructions = AdminJSONFormField(
        label="Instructions",
        help_text="Instructions dans différentes langues"
    )
    
    sentences = AdminJSONFormField(
        label="Phrases avec trous",
        help_text="Phrases avec ___ pour indiquer l'emplacement du trou"
    )
    
    answer_options = AdminJSONFormField(
        label="Options de réponse",
        help_text="Tableau d'options pour chaque langue"
    )
    
    correct_answers = AdminJSONFormField(
        label="Réponses correctes",
        help_text="Réponse correcte pour chaque langue"
    )
    
    hints = AdminJSONFormField(
        label="Indices",
        help_text="Indices optionnels pour chaque langue",
        required=False
    )
    
    explanations = AdminJSONFormField(
        label="Explications",
        help_text="Explications des réponses pour chaque langue",
        required=False
    )
    
    tags = AdminJSONFormField(
        label="Tags",
        help_text="Tags pour catégoriser l'exercice",
        required=False
    )
    
    class Meta:
        model = FillBlankExercise
        fields = '__all__'

@admin.register(FillBlankExercise)
class FillBlankExerciseAdmin(admin.ModelAdmin):
    """Interface d'administration pour les exercices à trous multilingues"""
    form = FillBlankExerciseAdminForm
    list_display = ('id', 'get_content_lesson', 'get_available_languages', 'difficulty', 'order', 'created_at')
    list_filter = ('difficulty', 'content_lesson__lesson__unit', 'created_at')
    search_fields = ('id', 'content_lesson__title_en', 'content_lesson__lesson__title_en')
    ordering = ('content_lesson', 'order')
    readonly_fields = ('created_at', 'updated_at', 'json_preview', 'lang_consistency_check')
    save_on_top = True
    
    fieldsets = (
        ('Relations', {
            'fields': ('content_lesson', 'order', 'difficulty')
        }),
        ('Contenu multilingue', {
            'fields': ('instructions', 'sentences', 'answer_options', 'correct_answers'),
            'description': 'Configurez le contenu dans différentes langues (EN, FR, ES, NL, etc.)'
        }),
        ('Aides pédagogiques', {
            'fields': ('hints', 'explanations'),
            'description': 'Facultatif - Aidez l\'utilisateur à comprendre l\'exercice',
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('tags', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Vérifications', {
            'fields': ('json_preview', 'lang_consistency_check'),
            'classes': ('collapse',),
        }),
    )
    
    def get_content_lesson(self, obj):
        """Afficher le titre de la leçon liée"""
        return obj.content_lesson.title_en
    get_content_lesson.short_description = 'Leçon'
    get_content_lesson.admin_order_field = 'content_lesson__title_en'
    
    def get_available_languages(self, obj):
        """Afficher les langues disponibles avec des badges colorés"""
        languages = obj.get_available_languages()
        
        # Mappings pour les noms complets des langues et couleurs
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
            # Ajoutez d'autres langues au besoin
        }
        
        colors = {
            'en': 'blue',
            'fr': 'red',
            'es': 'orange',
            'nl': 'purple',
            'de': 'green',
            'it': 'brown',
            'pt': 'teal',
            # Ajoutez d'autres couleurs au besoin
        }
        
        html = []
        for lang in languages:
            color = colors.get(lang, 'gray')
            name = language_names.get(lang, lang.upper())
            html.append(
                f'<span style="background-color: {color}; color: white; padding: 2px 6px; '
                f'border-radius: 3px; margin: 0 2px;">{name}</span>'
            )
        
        return format_html(' '.join(html) if html else 'Aucune langue')
    get_available_languages.short_description = 'Langues disponibles'
    
    def json_preview(self, obj):
        """Afficher un aperçu JSON formaté des données de l'exercice"""
        import json
        
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
    json_preview.short_description = 'Aperçu JSON'
    
    def lang_consistency_check(self, obj):
        """Vérifie la cohérence des langues entre les différents champs"""
        sentence_langs = set(obj.sentences.keys() if obj.sentences else [])
        answer_langs = set(obj.correct_answers.keys() if obj.correct_answers else [])
        options_langs = set(obj.answer_options.keys() if obj.answer_options else [])
        
        all_langs = sentence_langs.union(answer_langs).union(options_langs)
        
        # Créer un tableau HTML pour la vérification
        html = ['<table class="lang-consistency-table" style="width: 100%; border-collapse: collapse;">']
        
        # En-tête du tableau
        html.append('<thead><tr style="background-color: #417690; color: white;">')
        html.append('<th style="padding: 8px; text-align: left;">Langue</th>')
        html.append('<th style="padding: 8px;">Phrase</th>')
        html.append('<th style="padding: 8px;">Options</th>')
        html.append('<th style="padding: 8px;">Réponse</th>')
        html.append('<th style="padding: 8px;">État</th>')
        html.append('</tr></thead><tbody>')
        
        # Corps du tableau
        for lang in sorted(all_langs):
            has_sentence = lang in sentence_langs
            has_options = lang in options_langs
            has_answer = lang in answer_langs
            
            is_complete = has_sentence and has_options and has_answer
            status_label = 'Complet' if is_complete else 'Incomplet'
            bg_color = '#e8f5e9' if is_complete else '#ffebee'
            
            html.append(f'<tr style="background-color: {bg_color};">')
            html.append(f'<td style="padding: 8px; font-weight: bold;">{lang}</td>')
            html.append(f'<td style="padding: 8px; text-align: center;">{("✓" if has_sentence else "✗")}</td>')
            html.append(f'<td style="padding: 8px; text-align: center;">{("✓" if has_options else "✗")}</td>')
            html.append(f'<td style="padding: 8px; text-align: center;">{("✓" if has_answer else "✗")}</td>')
            
            status_color = '#2e7d32' if is_complete else '#c62828'
            html.append(f'<td style="padding: 8px; text-align: center; font-weight: bold; color: {status_color};">{status_label}</td>')
            html.append('</tr>')
        
        html.append('</tbody></table>')
        
        # Ajouter un résumé
        complete_langs = sum(1 for lang in all_langs if lang in sentence_langs and lang in options_langs and lang in answer_langs)
        
        html.append('<div style="margin-top: 15px; padding: 10px; background-color: #f9f9f9; border-radius: 4px;">')
        html.append(f'<p>{complete_langs} langues complètes sur {len(all_langs)} langues détectées.</p>')
        
        if complete_langs < len(all_langs):
            html.append('<p style="color: #c62828;">⚠️ Attention : certaines langues sont incomplètes.</p>')
        
        html.append('</div>')
        
        return format_html(''.join(html))
    lang_consistency_check.short_description = 'Vérification des langues'
    
    def save_model(self, request, obj, form, change):
        """Valider et nettoyer les données JSON avant enregistrement"""
        # Vérifier que les langues sont cohérentes entre sentences et correct_answers
        sentence_langs = set(obj.sentences.keys() if obj.sentences else [])
        answer_langs = set(obj.correct_answers.keys() if obj.correct_answers else [])
        options_langs = set(obj.answer_options.keys() if obj.answer_options else [])
        
        # Vérifier les incohérences
        missing_sentences = answer_langs.difference(sentence_langs)
        missing_answers = sentence_langs.difference(answer_langs)
        missing_options = sentence_langs.difference(options_langs)
        
        warnings = []
        
        if missing_sentences:
            warnings.append(f"Phrases manquantes pour les langues: {', '.join(missing_sentences)}")
        
        if missing_answers:
            warnings.append(f"Réponses correctes manquantes pour les langues: {', '.join(missing_answers)}")
            
        if missing_options:
            warnings.append(f"Options de réponse manquantes pour les langues: {', '.join(missing_options)}")
        
        # Afficher les avertissements
        for warning in warnings:
            self.message_user(
                request, 
                f"⚠️ {warning}",
                level='WARNING'
            )
        
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/json_prettify.css',)
        }
        js = ('admin/js/json_prettify.js',)



    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='fillblankexercise_import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv_view(self, request):
        """Vue pour importer des exercices à trous depuis un fichier CSV"""
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Importer des exercices à trous depuis CSV',
            'content_lessons': ContentLesson.objects.all().order_by('lesson__unit__level', 'lesson__unit__order', 'lesson__order', 'order'),
        }
        
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            content_lesson_id = request.POST.get('content_lesson')
            
            if not csv_file:
                messages.error(request, "Aucun fichier CSV sélectionné")
                return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
            
            if not content_lesson_id:
                messages.error(request, "Aucune leçon sélectionnée")
                return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
            
            try:
                content_lesson = ContentLesson.objects.get(id=content_lesson_id)
                
                # Lire le fichier CSV
                csv_data = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(csv_data))
                
                # Traiter chaque ligne
                exercises_created = []
                errors = []
                
                for i, row in enumerate(reader, start=1):
                    try:
                        # Préparer les données
                        languages = self._extract_languages_from_headers(reader.fieldnames)
                        
                        # Vérifications de base
                        if not self._validate_csv_row(row, languages):
                            errors.append(f"Ligne {i}: Données incomplètes ou invalides")
                            continue
                        
                        # Créer les dictionnaires pour chaque langue
                        sentences = {}
                        options = {}
                        answers = {}
                        
                        for lang in languages:
                            # Récupérer les données pour chaque langue
                            sentence_key = f'sentence_{lang}'
                            options_key = f'options_{lang}'
                            answer_key = f'answer_{lang}'
                            
                            if sentence_key in row and row[sentence_key]:
                                sentences[lang] = row[sentence_key]
                            
                            if options_key in row and row[options_key]:
                                # Convertir la liste d'options séparées par des virgules en tableau
                                options[lang] = [opt.strip() for opt in row[options_key].split(',')]
                            
                            if answer_key in row and row[answer_key]:
                                answers[lang] = row[answer_key]
                        
                        # Créer l'exercice
                        order = int(row.get('order', 1))
                        difficulty = row.get('difficulty', 'medium')
                        
                        # Récupérer les champs facultatifs
                        hints = {}
                        explanations = {}
                        
                        for lang in languages:
                            hint_key = f'hint_{lang}'
                            explanation_key = f'explanation_{lang}'
                            
                            if hint_key in row and row[hint_key]:
                                hints[lang] = row[hint_key]
                            
                            if explanation_key in row and row[explanation_key]:
                                explanations[lang] = row[explanation_key]
                        
                        # Créer ou mettre à jour l'exercice
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
                                'instructions': {
                                    lang: "Select the right answer." if lang == 'en' else "Sélectionnez la bonne réponse."
                                    for lang in languages
                                }
                            }
                        )
                        
                        exercises_created.append(exercise)
                    except Exception as e:
                        errors.append(f"Ligne {i}: {str(e)}")
                
                # Afficher les résultats
                if exercises_created:
                    messages.success(
                        request, 
                        f"{len(exercises_created)} exercices importés avec succès pour la leçon '{content_lesson.title_en}'"
                    )
                
                if errors:
                    messages.warning(
                        request, 
                        f"{len(errors)} erreurs lors de l'importation: {', '.join(errors[:5])}" +
                        (f"... et {len(errors) - 5} autres" if len(errors) > 5 else "")
                    )
                
                # Rediriger vers la liste des exercices
                return redirect('admin:course_fillblankexercise_changelist')
                
            except Exception as e:
                messages.error(request, f"Erreur lors de l'importation: {str(e)}")
        
        return TemplateResponse(request, "admin/fillblankexercise/import_csv.html", context)
    
    def _extract_languages_from_headers(self, headers):
        """Extrait les codes de langue depuis les en-têtes du CSV"""
        languages = set()
        
        for header in headers:
            if header.startswith(('sentence_', 'options_', 'answer_')):
                parts = header.split('_')
                if len(parts) >= 2:
                    lang = parts[1]
                    languages.add(lang)
        
        return languages
    
    def _validate_csv_row(self, row, languages):
        """Valide une ligne du CSV pour s'assurer qu'elle contient les données minimales requises"""
        # Vérifier qu'au moins une langue a des données complètes
        for lang in languages:
            sentence_key = f'sentence_{lang}'
            options_key = f'options_{lang}'
            answer_key = f'answer_{lang}'
            
            if (sentence_key in row and row[sentence_key] and
                options_key in row and row[options_key] and
                answer_key in row and row[answer_key]):
                return True
        
        return False
    
    # Ajouter un bouton d'importation dans la liste d'exercices
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)