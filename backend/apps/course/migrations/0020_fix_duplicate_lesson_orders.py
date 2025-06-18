from django.db import migrations

def fix_duplicate_lesson_orders(apps, schema_editor):
    """
    Fixes duplicate lesson orders by incrementing order values for duplicates.
    For each unit with duplicate orders, this function sorts lessons by ID
    and assigns new, sequential order values.
    """
    Lesson = apps.get_model('course', 'Lesson')
    
    # Group lessons by unit_id
    units_with_lessons = {}
    for lesson in Lesson.objects.all():
        unit_id = lesson.unit_id
        if unit_id not in units_with_lessons:
            units_with_lessons[unit_id] = []
        units_with_lessons[unit_id].append(lesson)
    
    # For each unit, find duplicate orders and fix them
    for unit_id, lessons in units_with_lessons.items():
        orders_seen = {}
        lessons_to_update = []
        
        # Sort lessons by ID to ensure consistent ordering
        lessons.sort(key=lambda l: l.id)
        
        for lesson in lessons:
            current_order = lesson.order
            
            if current_order in orders_seen:
                # This is a duplicate, find next available order
                max_order = max(orders_seen.keys())
                new_order = max_order + 1
                
                # Update order to next available
                lesson.order = new_order
                lessons_to_update.append(lesson)
                orders_seen[new_order] = True
            else:
                orders_seen[current_order] = True
        
        # Save all updated lessons
        for lesson in lessons_to_update:
            lesson.save()


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0019_lesson_updated_at'),
    ]

    operations = [
        migrations.RunPython(fix_duplicate_lesson_orders, reverse_code=migrations.RunPython.noop),
    ]