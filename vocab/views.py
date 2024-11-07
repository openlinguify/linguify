# vocab/views.py
from rest_framework import viewsets
from .models import Theme, Unit, Exercise, Vocabulary, UserVocabularyStatus
from .serializers import ThemeSerializer, UnitSerializer, ExerciseSerializer
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_word_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word_text = data.get('word')
        status = data.get('status')  # "learned" ou "to_review"

        # Rechercher le mot dans la base de données
        try:
            word = Vocabulary.objects.get(word=word_text)
            user = request.user

            # Mettre à jour ou créer le statut du mot pour l'utilisateur
            UserVocabularyStatus.objects.update_or_create(
                user=user,
                word=word,
                defaults={'status': status}
            )

            return JsonResponse({'message': 'Status updated successfully'})
        except Vocabulary.DoesNotExist:
            return JsonResponse({'error': 'Word not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

