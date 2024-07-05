from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from platforme.models import Categorie, Sous_categorie, Lesson, Activity, Vocabulaire, Video, Exercice, Test
from revision.models import Revision
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
def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    activity_views = {'Vocabulaire': vocabulaire_list, 'Video': video_list, 'Exercice': exercice_list, 'Test': test_list}
    view_function = activity_views.get(activity.type_activity)

    if view_function:
        return view_function(request, activity_id)
    else:
        return HttpResponseBadRequest(f"Unknown activity type: {activity.type_activity}")
def vocabulaire_list(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    vocabulaires = Vocabulaire.objects.filter(activity=activity)

    if request.method == 'POST':
        vocabulaire_ids_reviewed = request.POST.getlist('vocabulaire_reviewed')
        Vocabulaire.objects.filter(id__in=vocabulaire_ids_reviewed).update(reviewed=True)
        for vocabulaire_id in vocabulaire_ids_reviewed:
            vocabulaire = get_object_or_404(Vocabulaire, pk=vocabulaire_id)
            # Créer une révision si elle n'existe pas déjà
            if not Revision.objects.filter(vocabulaire=vocabulaire).exists():
                Revision.objects.create(vocabulaire=vocabulaire)

        # Rediriger vers la liste des activités une fois la révision terminée
        return HttpResponseRedirect(request.path_info)
    context = {
        'activity': activity,
        'vocabulaires': vocabulaires,
    }
    return render(request, 'platforme/vocabulaire_list.html', context)

def video_list(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    videos = Video.objects.filter(activity=activity)
    return render(request, 'platforme/video_list.html', {'activity': activity, 'videos': videos})
def exercice_list(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    exercices = Exercice.objects.filter(activity=activity)
    return render(request, 'platforme/exercice_list.html', {'activity': activity, 'exercices': exercices})
def test_list(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    tests = Test.objects.filter(activity=activity)
    return render(request, 'platforme/test_list.html', {'activity': activity, 'tests': tests})