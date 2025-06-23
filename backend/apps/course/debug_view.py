from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Chapter, Lesson, Unit

@login_required
def debug_data(request):
    """Vue de debug pour voir les données de la base"""
    
    # Compter les unités
    units_count = Unit.objects.count()
    
    # Compter les chapitres
    chapters_count = Chapter.objects.count()
    
    # Compter les leçons
    lessons_count = Lesson.objects.count()
    
    # Lister quelques chapitres avec leurs leçons
    chapters_debug = []
    for chapter in Chapter.objects.all()[:5]:
        lessons_in_chapter = Lesson.objects.filter(chapter=chapter).count()
        lessons_in_unit = Lesson.objects.filter(unit=chapter.unit, chapter__isnull=True).count()
        
        chapters_debug.append({
            'id': chapter.id,
            'title': chapter.title,
            'unit': chapter.unit.title if hasattr(chapter.unit, 'title') else str(chapter.unit),
            'lessons_direct': lessons_in_chapter,
            'lessons_unit_orphan': lessons_in_unit,
            'total_lessons': lessons_in_chapter + lessons_in_unit
        })
    
    # Lister quelques leçons
    lessons_debug = []
    for lesson in Lesson.objects.all()[:10]:
        lessons_debug.append({
            'id': lesson.id,
            'title': lesson.title,
            'unit': lesson.unit.title if hasattr(lesson.unit, 'title') else str(lesson.unit),
            'chapter': lesson.chapter.title if lesson.chapter else None,
            'has_content': lesson.content_lessons.exists()
        })
    
    return JsonResponse({
        'summary': {
            'units_count': units_count,
            'chapters_count': chapters_count,
            'lessons_count': lessons_count,
        },
        'chapters_sample': chapters_debug,
        'lessons_sample': lessons_debug
    })