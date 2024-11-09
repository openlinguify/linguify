from backend.django_apps.flashcard.models import Flashcard
from django.http import HttpResponse
from linguify.models import Vocabulary


# Create your views here.
def index(request):
    flashcards = Flashcard.objects.all()
    output = ', '.join([f.flashcard_title for f in flashcards])
    return HttpResponse(output)

def detail(request, flashcard_id):
    return HttpResponse(f"You're looking at flashcard {flashcard_id}")

def add_flashcard(request):
    flashcard = Flashcard(flashcard_title="New Flashcard")
    flashcard.save()
    return HttpResponse("Flashcard added")

def modify_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id)
    flashcard.modify_flashcard("Modified Flashcard")
    return HttpResponse("Flashcard modified")

def delete_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id)
    flashcard.delete()
    return HttpResponse("Flashcard deleted")

def add_vocabulary_to_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    flashcard.vocabulary.add(vocabulary_entry)
    return HttpResponse("Vocabulary entry added to flashcard")

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    self.vocabulary.add(vocabulary_entry)

def add_vocabulary_to_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    flashcard.vocabulary.add(vocabulary_entry)
    return HttpResponse("Vocabulary entry added to flashcard")
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    vocabulary_entry = Vocabulary.objects.get(id=1)
    self.vocabulary.add(vocabulary_entry)
