# course/admin.py
from django.contrib import admin
from .models import (
    Language,
    Level,
    LearningPath,
    Unit,
    Lesson,
    VocabularyList,
    ExerciseVocabularyMultipleChoice,
    ExerciseVocabularyFillBlank,
    ExerciseGrammarReordering,
    Exercise,
    GrammarRule,
    Grammar,
    GrammarRulePoint,
    Reading,
    Writing,
    TestRecap,
    TestRecapExercise,
    TestRecapAttempt,
    GrammarModule,
    GrammarRuleContent,
    GrammarRuleExercise,
)

admin.site.register(Language)
admin.site.register(Level)
admin.site.register(LearningPath)
admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(VocabularyList)
admin.site.register(ExerciseVocabularyMultipleChoice)
admin.site.register(ExerciseVocabularyFillBlank)
admin.site.register(ExerciseGrammarReordering)
admin.site.register(Exercise)
admin.site.register(Grammar)
admin.site.register(GrammarRulePoint)
admin.site.register(Reading)
admin.site.register(Writing)
admin.site.register(TestRecap)
admin.site.register(TestRecapExercise)
admin.site.register(TestRecapAttempt)
admin.site.register(GrammarModule)
admin.site.register(GrammarRuleContent)
admin.site.register(GrammarRuleExercise)
