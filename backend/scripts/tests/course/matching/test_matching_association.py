# Script to test matching exercise association
# Run with: python manage.py shell < test_matching_association.py

from apps.course.models import MatchingExercise, ContentLesson, VocabularyList, Lesson

print("=== Testing Matching Exercise Association ===")

# Get the first lesson
lesson = Lesson.objects.get(id=1)
print(f"\nLesson: {lesson.title_en}")

# Get vocabulary content lessons
vocab_lessons = ContentLesson.objects.filter(
    lesson=lesson,
    content_type__icontains='vocabulary'
)
print(f"Vocabulary ContentLessons found: {vocab_lessons.count()}")

for vl in vocab_lessons:
    vocab_count = VocabularyList.objects.filter(content_lesson=vl).count()
    print(f"  - {vl.title_en}: {vocab_count} words")

# Get matching content lessons
matching_lessons = ContentLesson.objects.filter(
    lesson=lesson,
    content_type__icontains='matching'
)
print(f"\nMatching ContentLessons found: {matching_lessons.count()}")

for ml in matching_lessons:
    print(f"  - {ml.title_en}")
    exercises = MatchingExercise.objects.filter(content_lesson=ml)
    print(f"    Exercises: {exercises.count()}")
    
    for ex in exercises:
        print(f"      Exercise {ex.id}: {ex.vocabulary_words.count()} words")
        
        # Test the find_vocabulary_for_matching method
        vocab_found = VocabularyList.find_vocabulary_for_matching(
            content_lesson=ml,
            parent_lesson=lesson,
            limit=8
        )
        print(f"      Vocabulary available: {vocab_found.count()}")
        
        # Try to associate
        if vocab_found.exists() and ex.vocabulary_words.count() == 0:
            print("      Associating vocabulary...")
            result = ex.auto_associate_vocabulary(force_update=True)
            print(f"      Associated: {result} words")
            print(f"      Final count: {ex.vocabulary_words.count()}")

print("\n=== Test Complete ===")