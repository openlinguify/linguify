from django.contrib import admin
from .models import Quiz, Question, Answer, QuizSession, QuizResult


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['text', 'is_correct', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_type', 'text', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['text', 'quiz__title']
    inlines = [AnswerInline]
    ordering = ['quiz', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'difficulty', 'is_public', 'created_at']
    list_filter = ['category', 'difficulty', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'category', 'difficulty')
        }),
        ('Paramètres', {
            'fields': ('is_public', 'time_limit', 'creator')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'started_at', 'completed_at', 'score', 'total_points']
    list_filter = ['completed_at', 'quiz__category']
    search_fields = ['user__username', 'quiz__title']
    date_hierarchy = 'started_at'
    readonly_fields = ['started_at', 'score', 'total_points', 'time_spent']


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct']
    search_fields = ['session__user__username', 'question__text']
    readonly_fields = ['is_correct', 'points_earned']