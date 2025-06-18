# Debug script to check content_type values
# Run with: python manage.py shell < debug_content_type.py

from apps.course.models import ContentLesson

print("=== Content Type Debug ===")

# Get all unique content types
content_types = ContentLesson.objects.values_list('content_type', flat=True).distinct()
print("\nAll unique content_type values:")
for ct in content_types:
    count = ContentLesson.objects.filter(content_type=ct).count()
    print(f"  '{ct}': {count} content lessons")

# Check specific lesson
lesson_id = 1  # Lesson 1
print(f"\nContent types in Lesson {lesson_id}:")
content_lessons = ContentLesson.objects.filter(lesson_id=lesson_id).order_by('order')
for cl in content_lessons:
    print(f"  {cl.id}: '{cl.content_type}' - {cl.title_en}")

# Check the ContentLesson choices
print("\nContentLesson CONTENT_TYPE choices:")
for choice in ContentLesson.CONTENT_TYPE:
    print(f"  {choice[0]}: {choice[1]}")

print("\n=== End Debug ===")