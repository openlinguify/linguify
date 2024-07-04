from django.shortcuts import render, get_object_or_404
from platforme.models import Categorie, Sous_categorie, Lesson, Activity, Vocabulaire, Video, Exercice, Test

def platforme(request):
    categories = Categorie.objects.all()
    sous_categories = Sous_categorie.objects.select_related('categorie').all()
    return render(request,
                  'platforme/platforme.html',
                  context={
                      'categories': categories,
                      'sous_categories': sous_categories,
                  })
def lesson_list(request, sous_categorie_id):
    categories = Categorie.objects.all()
    sous_categorie = get_object_or_404(Sous_categorie, id=sous_categorie_id)
    lessons = Lesson.objects.filter(sous_categorie=sous_categorie)
    return render(request,
                  'platforme/lesson_list.html',
                  context={
                      'categories': categories,
                      'sous_categorie': sous_categorie,
                      'lessons': lessons,
                  })
def activity_list(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    activities = Activity.objects.filter(lesson=lesson)

    context = {
        'lesson': lesson,
        'activities': activities,
    }
    return render(request, 'platforme/activity_list.html', context)

def vocabulaire_list(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    vocabulaires = Vocabulaire.objects.filter(activity=activity)

    context = {
        'activity': activity,
        'vocabulaires': vocabulaires,
    }
    return render(request, 'platforme/vocabulaire_list.html', context)

