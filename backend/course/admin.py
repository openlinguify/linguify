# course/admin.py
from django.contrib import admin
from .models import (
    Unit, 
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    ExerciseVocabularyMultipleChoice, 
    MultipleChoiceQuestion, 
    Numbers
)

admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(ContentLesson)
admin.site.register(TheoryContent)
admin.site.register(VocabularyList)
admin.site.register(Numbers)
admin.site.register(MultipleChoiceQuestion)
admin.site.register(ExerciseVocabularyMultipleChoice)