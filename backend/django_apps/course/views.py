from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from linguify.models import Vocabulary, Grammar, Courses_languages, Courses_languages_categories
from django.contrib.auth.decorators import login_required
import random

from linguify.serializers import CoursesLanguagesSerializer, CoursesLanguagesCategorySerializer
from backend.django_apps.quiz.models import Quiz


def base(request):
    return render(request, '../../../frontend/public/templates_storage/base.html')

@login_required
def home(request):
    return render(request, 'linguify/home.html')
def index(request):
    return render(request, 'index.html')
def dashboard(request):
    return render(request, 'dashboard.html')
def header(request):
    return render(request,
                  'header.html',
                  {'header': 'header'}
    )
def footer(request):
    return render(request, 'footer.html')
def vocabulaire(request):
    return render(request, 'vocabulaire.html')
def exercice_vocabulary(request):
    # Sélectionner un mot aléatoire
    random_word = random.choice(Vocabulary.objects.all())

    # Sélectionner trois autres mots de la base de données
    other_words = Vocabulary.objects.exclude(pk=random_word.pk).order_by('?')[:3]

    # Mélanger la liste des mots
    words = list(other_words) + [random_word]
    random.shuffle(words)

    context = {
        'word': random_word,
        'choices': words,
    }
    return render(request, 'exercice_vocabulaire.html', context)
def grammaire(request):

    return render(request,
                  'grammaire.html',
                  {'vocabulaires': Vocabulary.objects.all(), 'grammaires': Grammar.objects.all()
    })
def revision(request):
    return render(request, 'revision.html')
def quiz(request, quiz_id=None):
    if request.user.is_authenticated:
        learning_language = request.user.learning_language
        level = request.user.level_target_language

        if not learning_language or not level:
            return HttpResponse("Please specify the learning language and level in your profile.")

        # Get vocabulary words
        vocabulary_words = Vocabulary.objects.filter(language_id=learning_language, level_target_language=level)
        if not vocabulary_words.exists():
            return HttpResponse("No words found for the specified learning language and level.")

        # Select a random word pair
        word_pair = random.choice(vocabulary_words)
        word = word_pair.word
        correct_translation = word_pair.translation

        # Get three incorrect translations
        incorrect_translations = Quiz.objects.filter(language_id=learning_language.language_code, level=level).exclude(pk=(quiz_id)).values_list('translation', flat=True)[:3]
        options = list(incorrect_translations) + [correct_translation]
        random.shuffle(options)
        context = {
            'language': learning_language,
            'word': word,
            'options': options,
            'correct_translation': correct_translation
        }
        return render(request, 'quiz.html', context)
    else:
        return HttpResponse("Please log in to access this feature.")
def check_answer(request):
    if request.method == 'POST':
        selected_translation = request.POST.get('selected_translation')
        correct_translation = request.POST.get('correct_translation')
        if selected_translation == correct_translation:
            result = "Correct!"
        else:
            result = "Incorrect!"
        context = {
            'result': result,
            'correct_translation': correct_translation
        }
        return render(request, 'result.html', context)
    else:
        return HttpResponse("Method Not Allowed")
def testlinguisitique(request):
    return render(request, 'testlinguistique.html')
def courses(request):
    # Récupérer tous les cours depuis la base de données
    courses = Courses_languages.objects.all()
    # Créer une liste de noms et de descriptions des cours
    course_names = [course.name for course in courses]
    course_description = [course.definition for course in courses]
    # Passer les données au modèle
    context = {
        'course_names': course_names,
        'course_description': course_description,
    }
    # Rendre le modèle avec les données
    return render(request, 'linguify/courses.html', context)
def prices(request):
    return render(request, 'linguify/prices.html')
def contact(request):
    return render(request, 'linguify/contact.html')
def about(request):
    return render(request, 'linguify/about.html')
def search_vocabulary(request):
    if request.method == 'GET':
        # Get the search query from the request
        query = request.GET.get('query')
        if query:
            # Filter the vocabularies based on the search query
            vocabulary_list = Vocabulary.objects.filter(word__icontains=query)
        else:
            # If no query is provided, return all vocabularies
            vocabulary_list = Vocabulary.objects.all()

        context = {
            'vocabularies': vocabulary_list,
            'query': query,
        }
        return render(request, 'linguify/search_vocabulary.html', context)

class Courses_languagesViewSet(viewsets.ModelViewSet):
    serializer_class = CoursesLanguagesSerializer
    queryset = Courses_languages.objects.all()

class Courses_languages_categoriesViewSet(viewsets.ModelViewSet):
    serializer_class = CoursesLanguagesCategorySerializer
    queryset = Courses_languages_categories.objects.all()

    from django.shortcuts import render, get_object_or_404
    from django.http import HttpResponseBadRequest, HttpResponseRedirect
    from platforme.models import Categorie, Sous_categorie, Lesson, Activity, Vocabulaire, Video, Exercice, Test
    from revision.models import Revision
    def platforme(request):
        categories = Categorie.objects.all()
        sous_categories = Sous_categorie.objects.select_related('categorie').all()
        return render(request,
                      '../old_docs/../frontend/public/templates_storage/templates/platforme/platforme.html',
                      context={
                          'categories': categories,
                          'sous_categories': sous_categories,
                      })

    def lesson_list(request, sous_categorie_id):
        categories = Categorie.objects.all()
        sous_categorie = get_object_or_404(Sous_categorie, id=sous_categorie_id)
        lessons = Lesson.objects.filter(sous_categorie=sous_categorie)
        return render(request,
                      '../old_docs/../frontend/public/templates_storage/templates/platforme/lesson_list.html',
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
        return render(request,
                      '../old_docs/../frontend/public/templates_storage/templates/platforme/activity_list.html',
                      context)

    def activity(request, activity_id):
        activity = get_object_or_404(Activity, pk=activity_id)
        activity_views = {'Vocabulaire': vocabulaire_list, 'Video': video_list, 'Exercice': exercice_list,
                          'Test': test_list}
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
        return render(request,
                      '../old_docs/../frontend/public/templates_storage/templates/platforme/vocabulaire_list.html',
                      context)

    def video_list(request, activity_id):
        activity = get_object_or_404(Activity, pk=activity_id)
        videos = Video.objects.filter(activity=activity)
        return render(request, '../old_docs/../frontend/public/templates_storage/templates/platforme/video_list.html',
                      {'activity': activity, 'videos': videos})

    def exercice_list(request, activity_id):
        activity = get_object_or_404(Activity, pk=activity_id)
        exercices = Exercice.objects.filter(activity=activity)
        return render(request,
                      '../old_docs/../frontend/public/templates_storage/templates/platforme/exercice_list.html',
                      {'activity': activity, 'exercices': exercices})

    def test_list(request, activity_id):
        activity = get_object_or_404(Activity, pk=activity_id)
        tests = Test.objects.filter(activity=activity)
        return render(request, '../old_docs/../frontend/public/templates_storage/templates/platforme/test_list.html',
                      {'activity': activity, 'tests': tests})