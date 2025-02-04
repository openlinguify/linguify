# course/admin.py
from django.contrib import admin
from .models import Unit, Lesson, ContentLesson, VocabularyList, ExerciseVocabularyMultipleChoice, MultipleChoiceQuestion

admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(ContentLesson)
admin.site.register(VocabularyList)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(ExerciseVocabularyMultipleChoice)
