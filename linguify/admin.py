from django.contrib import admin
from .models import (
    Language,
    Courses_languages_categories,
    Courses_languages,
    Courses_subcategories,
    Vocabulary,
    Grammar,
    Units,
    Theme,
    UserLessonProgress,
    Revision,
    UserRevisionProgress,
    Quiz
)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language',)
    search_fields = ('language',)

@admin.register(Courses_languages_categories)
class CoursesLanguagesCategoriesAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'category_description')
    search_fields = ('category_name',)

@admin.register(Courses_languages)
class CoursesLanguagesAdmin(admin.ModelAdmin):
    list_display = ('course_languages_id', 'course_languages_title', 'category')
    search_fields = ('course_languages_title',)
    list_filter = ('category',)

@admin.register(Courses_subcategories)
class CoursesSubcategoriesAdmin(admin.ModelAdmin):
    list_display = ('subcategory_id', 'subcategory_title', 'category_id')
    search_fields = ('subcategory_title',)
    list_filter = ('category_id',)

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('vocabulary_id', 'vocabulary_title', 'word', 'translation')
    search_fields = ('vocabulary_title', 'word')

@admin.register(Grammar)
class GrammarAdmin(admin.ModelAdmin):
    list_display = ('grammar_id', 'grammar_title', 'grammar_description')
    search_fields = ('grammar_title',)

@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ('unit_id', 'unit_title', 'course_id', 'subcategory_id', 'unit_type')
    search_fields = ('unit_title',)
    list_filter = ('course_id', 'subcategory_id')

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme_name', 'theme_description')
    search_fields = ('theme_name',)

@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user_lesson_progress_id', 'user_id', 'course_id', 'unit_id', 'statut', 'percentage_completion')
    search_fields = ('user_id__username', 'course_id__course_languages_title')
    list_filter = ('statut', 'course_id')

@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('revision_id', 'revision_title', 'word', 'translation', 'last_revision_date')
    search_fields = ('revision_title', 'word')

@admin.register(UserRevisionProgress)
class UserRevisionProgressAdmin(admin.ModelAdmin):
    list_display = ('user_revision_progress_id', 'user_id', 'revision_id', 'statut', 'percentage_completion')
    search_fields = ('user_id__username', 'revision_id__revision_title')
    list_filter = ('statut',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_id', 'user_id', 'word', 'correct_translation', 'is_completed', 'created_at')
    search_fields = ('user_id__username', 'word')
    list_filter = ('is_completed',)