from apps.course.models import ContentLesson, TheoryContent

# Vérifier si "Dates - Theory - theory - 2" a déjà un TheoryContent
content_lesson = ContentLesson.objects.filter(title_en__contains="Dates").first()
if content_lesson:
    print(f"ContentLesson: {content_lesson}")
    has_theory = TheoryContent.objects.filter(content_lesson=content_lesson).exists()
    print(f"Has TheoryContent: {has_theory}")
    
    if has_theory:
        theory = TheoryContent.objects.get(content_lesson=content_lesson)
        print(f"Existing TheoryContent ID: {theory.id}")
        print(f"Content EN: {theory.content_en[:50]}...")
else:
    print("ContentLesson 'Dates' not found")