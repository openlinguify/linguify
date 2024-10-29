from django.contrib import admin
from .models import Flashcard, UserFlashcardProgress

class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('flashcard_id', 'user', 'flashcard_title', 'vocabulary', 'theme', 'image_flashcard')
    search_fields = ('flashcard_title', 'vocabulary__word', 'user__username')
    list_filter = ('theme',)

class UserFlashcardProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'flashcard', 'statut', 'percentage_completion', 'score_flashcard', 'time_study')
    search_fields = ('user__username', 'flashcard__flashcard_title')
    list_filter = ('statut', 'percentage_completion')

# Enregistrer les modèles dans l'admin
admin.site.register(Flashcard, FlashcardAdmin)
admin.site.register(UserFlashcardProgress, UserFlashcardProgressAdmin)
