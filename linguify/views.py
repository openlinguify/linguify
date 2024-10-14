# linguify/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import random

from linguify.models import (
    CourseLanguage, Vocabulary, Grammar, Unit, UserLessonProgress,
    Revision, UserRevisionProgress, Quiz, Flashcard, UserFlashcardProgress
)
from linguify.forms import ThemeForm

def base(request):
    return render(request, 'base.html')

@login_required
def home(request):
    return render(request, 'linguify/home.html')

def index(request):
    return render(request, 'linguify/index.html')

def dashboard(request):
    return render(request, 'linguify/dashboard.html')

def header(request):
    return render(request, 'linguify/header.html', {'header': 'header'})

def footer(request):
    return render(request, 'linguify/footer.html')

@login_required
def vocabulaire(request):
    learning_language = request.user.learning_language
    level = request.user.level_target_language

    if not learning_language or not level:
        return HttpResponse("Please specify your learning language and level in your profile.")

    vocabularies = Vocabulary.objects.filter(language=learning_language, level=level)
    context = {'vocabularies': vocabularies}
    return render(request, 'linguify/vocabulaire.html', context)

@login_required
def exercice_vocabulary(request):
    learning_language = request.user.learning_language
    level = request.user.level_target_language

    if not learning_language or not level:
        return HttpResponse("Please specify your learning language and level in your profile.")

    vocabularies = Vocabulary.objects.filter(language=learning_language, level=level)
    if not vocabularies.exists():
        return HttpResponse("No vocabulary words available for your language and level.")

    random_word = random.choice(vocabularies)
    other_words = vocabularies.exclude(pk=random_word.pk).order_by('?')[:3]

    if other_words.count() < 3:
        other_words = Vocabulary.objects.exclude(pk=random_word.pk).order_by('?')[:3]

    choices = list(other_words) + [random_word]
    random.shuffle(choices)

    context = {
        'word': random_word,
        'choices': choices,
    }
    return render(request, 'linguify/exercice_vocabulaire.html', context)

@login_required
def grammaire(request):
    learning_language = request.user.learning_language
    level = request.user.level_target_language

    if not learning_language or not level:
        return HttpResponse("Please specify your learning language and level in your profile.")

    vocabularies = Vocabulary.objects.filter(language=learning_language, level=level)
    grammars = Grammar.objects.filter(language=learning_language, level=level)

    context = {
        'vocabularies': vocabularies,
        'grammars': grammars,
    }
    return render(request, 'linguify/grammaire.html', context)

@login_required
def revision(request):
    learning_language = request.user.learning_language
    level = request.user.level_target_language

    if not learning_language or not level:
        return HttpResponse("Please specify your learning language and level in your profile.")

    revisions = Revision.objects.filter(language=learning_language, level=level)
    context = {'revisions': revisions}
    return render(request, 'linguify/revision.html', context)

@login_required
def quiz(request):
    learning_language = request.user.learning_language
    level = request.user.level_target_language

    if not learning_language or not level:
        return HttpResponse("Please specify the learning language and level in your profile.")

    vocabulary_words = Vocabulary.objects.filter(language=learning_language, level=level)
    if not vocabulary_words.exists():
        return HttpResponse("No words found for the specified learning language and level.")

    word_pair = random.choice(vocabulary_words)
    word = word_pair.word
    correct_translation = word_pair.translation

    incorrect_words = vocabulary_words.exclude(pk=word_pair.pk).order_by('?')[:3]
    if incorrect_words.count() < 3:
        incorrect_words = Vocabulary.objects.exclude(pk=word_pair.pk).order_by('?')[:3]

    incorrect_translations = [v.translation for v in incorrect_words]
    options = incorrect_translations + [correct_translation]
    random.shuffle(options)

    context = {
        'language': learning_language,
        'word': word,
        'options': options,
        'correct_translation': correct_translation,
    }
    return render(request, 'linguify/quiz.html', context)

def check_answer(request):
    if request.method == 'POST':
        selected_translation = request.POST.get('selected_translation')
        correct_translation = request.POST.get('correct_translation')
        result = "Correct!" if selected_translation == correct_translation else "Incorrect!"
        context = {
            'result': result,
            'correct_translation': correct_translation,
        }
        return render(request, 'linguify/result.html', context)
    else:
        return HttpResponse("Method Not Allowed")

def testlinguistique(request):
    return render(request, 'linguify/testlinguistique.html')

def courses(request):
    courses = CourseLanguage.objects.all()
    context = {'courses': courses}
    return render(request, 'linguify/courses.html', context)

def prices(request):
    return render(request, 'linguify/prices.html')

def contact(request):
    return render(request, 'linguify/contact.html')

def about(request):
    return render(request, 'linguify/about.html')

@login_required
def search_vocabulary(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        learning_language = request.user.learning_language
        level = request.user.level_target_language

        if not learning_language or not level:
            return HttpResponse("Please specify your learning language and level in your profile.")

        vocabularies = Vocabulary.objects.filter(language=learning_language, level=level)
        if query:
            vocabularies = vocabularies.filter(word__icontains=query)

        context = {
            'vocabularies': vocabularies,
            'query': query,
        }
        return render(request, 'linguify/search_vocabulary.html', context)
    else:
        return HttpResponse("Method Not Allowed")

@login_required
def add_vocabulary_to_flashcard(request, flashcard_id):
    if request.method == 'POST':
        vocabulary_id = request.POST.get('vocabulary_id')
        flashcard = get_object_or_404(Flashcard, id=flashcard_id, user=request.user)
        vocabulary_entry = get_object_or_404(Vocabulary, id=vocabulary_id)
        flashcard.vocabulary.add(vocabulary_entry)
        return redirect('flashcard_detail', flashcard_id=flashcard_id)
    else:
        return HttpResponse("Method Not Allowed")
