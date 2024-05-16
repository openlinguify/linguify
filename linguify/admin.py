from django.contrib import admin
from linguify.models import Courses_languages, Courses_languages_categories, Courses_subcategories, Vocabulary, Grammar, Units, User_Lesson_Progress, Flashcards, User_Flashcard_Progress, Revision, User_Revision_Progress
from django.contrib.auth.models import User
from authentication.models import Language, LevelTarget, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
class Courses_languagesAdmin(admin.ModelAdmin):
    list_display = ('course_languages_id', 'language_id', 'course_languages_title')
class Courses_categoriesAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'category_description')
class Courses_subcategoriesAdmin(admin.ModelAdmin):
    list_display = ('subcategory_id', 'subcategory_title', 'subcategory_description', 'category_id')
class UnitsAdmin(admin.ModelAdmin):
    list_display = ('unit_id', 'unit_title', 'unit_description', 'course_id', 'subcategory_id', 'unit_type')
class User_Lesson_ProgressAdmin(admin.ModelAdmin):
    list_display = ('user_lesson_progress_id', 'user_id', 'course_id', 'unit_id', 'statut', 'pourcentage_completion', 'time_study', 'score_revision', 'score_exercise', 'score_quiz')
class FlashcardsAdmin(admin.ModelAdmin):
    list_display = ('flashcard_id', 'user_id', 'language_id', 'level_target_language', 'flashcard_title')
class User_Flashcard_ProgressAdmin(admin.ModelAdmin):
    list_display = ('user_flashcard_progress_id', 'user_id', 'flashcard_id', 'statut', 'pourcentage_completion', 'time_study', 'score_flashcard')
class RevisionAdmin(admin.ModelAdmin):
    list_display = ('revision_id', 'language_id', 'level_target_language', 'revision_title', 'revision_description')
class User_Revision_ProgressAdmin(admin.ModelAdmin):
    list_display = ('user_revision_progress_id', 'user_id', 'revision_id', 'statut', 'pourcentage_completion', 'time_study', 'score_revision')
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_id', 'language_id', 'level_target_language', 'quiz_title', 'quiz_description')

######################################
admin.site.register(Courses_languages, Courses_languagesAdmin)
admin.site.register(Courses_languages_categories, Courses_categoriesAdmin)
admin.site.register(Courses_subcategories, Courses_subcategoriesAdmin)
admin.site.register(Units, UnitsAdmin)
admin.site.register(User_Lesson_Progress, User_Lesson_ProgressAdmin)
admin.site.register(Flashcards, FlashcardsAdmin)
admin.site.register(User_Flashcard_Progress, User_Flashcard_ProgressAdmin)
admin.site.register(Revision, RevisionAdmin)
admin.site.register(User_Revision_Progress, User_Revision_ProgressAdmin)
admin.site.register(User, UserAdmin)
######################################

