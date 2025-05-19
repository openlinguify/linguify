#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import TestRecap, ContentLesson, Lesson

# Debug pour la leçon 162
lesson_id = 162

print(f"\n=== Debug pour la leçon {lesson_id} ===")

# 1. Obtenir la leçon
try:
    lesson = Lesson.objects.get(id=lesson_id)
    print(f"\nLesson: {lesson.title_en} (ID: {lesson.id})")
except Lesson.DoesNotExist:
    print(f"Lesson {lesson_id} not found!")
    sys.exit(1)

# 2. Voir tous les ContentLessons de type test_recap pour cette leçon
content_lessons = ContentLesson.objects.filter(
    lesson=lesson,
    content_type='test_recap'
)
print(f"\nContentLessons avec type 'test_recap': {content_lessons.count()}")
for cl in content_lessons:
    print(f"  - ID: {cl.id}, Title: {cl.title_en}")

# 3. Voir tous les TestRecaps pour cette leçon
test_recaps = TestRecap.objects.filter(lesson=lesson)
print(f"\nTestRecaps pour cette leçon: {test_recaps.count()}")
for tr in test_recaps:
    print(f"  - ID: {tr.id}, Title: {tr.title_en}")
    
    # Vérifier si l'admin afficherait "In Content" pour ce TestRecap
    has_content = ContentLesson.objects.filter(
        lesson=tr.lesson,
        content_type='test_recap'
    ).exists()
    print(f"    In Content: {'✓' if has_content else '✗'}")
    print(f"    Questions: {tr.questions.count()}")

# 4. Vérifier spécifiquement le ContentLesson 92
print("\n=== ContentLesson 92 spécifique ===")
try:
    cl_92 = ContentLesson.objects.get(id=92)
    print(f"ContentLesson 92:")
    print(f"  Type: {cl_92.content_type}")
    print(f"  Lesson: {cl_92.lesson.title_en} (ID: {cl_92.lesson.id})")
    print(f"  Title: {cl_92.title_en}")
    
    # Y a-t-il un TestRecap avec le même titre?
    matching_test_recaps = TestRecap.objects.filter(
        lesson=cl_92.lesson,
        title_en=cl_92.title_en
    )
    print(f"\nTestRecaps avec le même titre: {matching_test_recaps.count()}")
    for tr in matching_test_recaps:
        print(f"  - ID: {tr.id}")
        
except ContentLesson.DoesNotExist:
    print("ContentLesson 92 not found!")

# 5. Voir TOUS les TestRecaps créés
print("\n=== TOUS les TestRecaps ===")
all_test_recaps = TestRecap.objects.all().order_by('-created_at')[:10]
for tr in all_test_recaps:
    print(f"ID: {tr.id}, Title: {tr.title_en}, Lesson: {tr.lesson.title_en if tr.lesson else 'None'}")