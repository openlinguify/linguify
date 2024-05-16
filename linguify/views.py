from django.shortcuts import render
from django.http import HttpResponse
from linguify.models import Courses_languages, Courses_languages_categories, Courses_subcategories, Vocabulary, Grammar, Units, User_Lesson_Progress, Revision, User_Revision_Progress, Quiz, Flashcards, User_Flashcard_Progress
from linguify.forms import ThemeForm
from django.contrib.auth.decorators import login_required
from authentication.models import User
import random

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View

def base(request):
    return render(request, 'base.html')

@login_required
def home(request):
    return render(request, 'linguify/home.html')

# Create your views here.
def index(request):
    return render(request, 'index.html')

def header(request):
    return render(request,
                  'header.html',
                  {'header': 'header'}
    )

def footer(request):
    return render(request, 'footer.html')

def vocabulaire(request):
    vocabulaires = Vocabulary.objects.all()
    form = ThemeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            theme = form.cleaned_data['theme']
            if theme:
                vocabulaires = Vocabulary.objects.filter(theme=theme)
                if not vocabulaires:
                    # Redirect with error message if no vocabularies found
                    return render(request, 'vocabulaire.html', {'form': form, 'error': True})
            else:
                vocabulaires = Vocabulary.objects.all()  # Show all vocabularies if no theme selected
        else:
            # Redirect with error message if form is invalid
            return render(request, 'vocabulaire.html', {'form': form, 'error': True})

    return render(request, 'vocabulaire.html', {'form': form, 'vocabulaires': vocabulaires})

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
    return HttpResponse("""
                        <h1>About</h1>
                        <p>Linguify is a language school that offers courses in English, French, Dutch, German, Italian, and Spanish.</p>
                        <p>Our teachers are native speakers and have years of experience in teaching languages.</p>
                        <p>Our goal is to help you improve your language skills and achieve your language learning goals.</p>
                        <p>Whether you are a beginner or an advanced learner, we have a course that is right for you.</p>
                        <p>Our classes are small and interactive, so you will have plenty of opportunities to practice speaking and listening.</p>
                        <p>We also offer private lessons and exam preparation courses.</p>
                        <p>Contact us today to learn more about our courses and schedule a free trial lesson.</p>
                        """)

#let's integrate the search functionality into a Django view and return the filtered results to the frontend. Here's how you can do it:
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

def revision(request):
    return render(request, 'revision.html')

def add_vocabulary_to_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    flashcard.vocabulary.add(vocabulary_entry)
    return HttpResponse("Vocabulary entry added to flashcard")

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    self.vocabulary.add(vocabulary_entry)
def quiz(request):
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