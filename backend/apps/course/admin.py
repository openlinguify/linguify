# course/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Unit, 
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    ExerciseVocabularyMultipleChoice, 
    MultipleChoiceQuestion, 
    Numbers,
    ExerciseGrammarReordering
)

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