from django.contrib import admin
from linguify.models import Courses_languages, Courses_languages_categories, Courses_subcategories, Vocabulary, Grammar, Units, UserLessonProgress, Flashcard, UserFlashcardProgress, Revision, UserRevisionProgress


class Courses_languagesAdmin(admin.ModelAdmin):
    list_display = ('course_languages_id', 'language_id', 'course_languages_title')
class Courses_categoriesAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'category_description')
class Courses_subcategoriesAdmin(admin.ModelAdmin):
    list_display = ('subcategory_id', 'subcategory_title', 'subcategory_description', 'category_id')
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('vocabulary_id', 'language_id', 'level', 'vocabulary_title', 'word', 'translation', 'example_sentence')
class GrammarAdmin(admin.ModelAdmin):
    list_display = ('grammar_id', 'language_id', 'level', 'grammar_title', 'grammar_description')
class UnitsAdmin(admin.ModelAdmin):
    list_display = ('unit_id', 'unit_title', 'unit_description', 'course_id', 'subcategory_id', 'unit_type')
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user_lesson_progress_id', 'user_id', 'course_id', 'unit_id', 'statut', 'percentage_completion', 'time_study', 'score_revision', 'score_exercise', 'score_quiz')
class FlashcardsAdmin(admin.ModelAdmin):
    list_display = ('flashcard_id', 'user_id', 'language_id', 'level', 'flashcard_title', 'image_flashcard')
class User_Flashcard_ProgressAdmin(admin.ModelAdmin):
    list_display = ('user_flashcard_progress_id', 'user_id', 'flashcard_id', 'statut', 'percentage_completion', 'time_study', 'score_flashcard')
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('revision_id', 'language_id', 'level', 'revision_title', 'revision_description')
class UserRevisionProgressAdmin(admin.ModelAdmin):
    list_display = ('user_revision_progress_id', 'user_id', 'revision_id', 'statut', 'percentage_completion', 'time_study', 'score_revision')
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_id', 'language_id', 'level', 'quiz_title', 'quiz_description')

######################################
admin.site.register(Courses_languages, Courses_languagesAdmin)
admin.site.register(Courses_languages_categories, Courses_categoriesAdmin)
admin.site.register(Courses_subcategories, Courses_subcategoriesAdmin)
admin.site.register(Vocabulary, VocabularyAdmin)
admin.site.register(Grammar, GrammarAdmin)
admin.site.register(Units, UnitsAdmin)
admin.site.register(UserLessonProgress, UserLessonProgressAdmin)
admin.site.register(Flashcard, FlashcardsAdmin)
admin.site.register(UserFlashcardProgress, User_Flashcard_ProgressAdmin)
admin.site.register(Revision, RevisionAdmin)
admin.site.register(UserRevisionProgress, UserRevisionProgressAdmin)

######################################

