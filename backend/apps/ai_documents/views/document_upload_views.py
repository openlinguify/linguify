"""
Vues pour l'upload de documents et la génération automatique de flashcards
"""

import mimetypes
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator

from apps.revision.models import FlashcardDeck, Flashcard
from ..models import DocumentUpload
from ..utils.text_extraction import extract_text_from_file, preprocess_text_for_flashcards, detect_document_language
from ..services import FlashcardGeneratorService


@method_decorator(login_required, name='dispatch')
class DocumentUploadView(View):
    """
    Vue principale pour l'upload de documents et génération de flashcards
    """

    def get(self, request):
        """Affiche la page d'upload"""
        # Récupérer les decks de l'utilisateur
        user_decks = FlashcardDeck.objects.filter(user=request.user, is_active=True)

        # Récupérer les uploads récents
        recent_uploads = DocumentUpload.objects.filter(user=request.user)[:10]

        context = {
            'decks': user_decks,
            'recent_uploads': recent_uploads,
        }

        return render(request, 'ai_documents/upload.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def process_document(request):
    """
    Traite un document uploadé et génère des flashcards

    Cette vue est conçue pour fonctionner avec HTMX
    """
    try:
        # Récupérer le fichier et les paramètres
        uploaded_file = request.FILES.get('document')
        deck_id = request.POST.get('deck_id')
        max_cards = int(request.POST.get('max_cards', 10))
        create_new_deck = request.POST.get('create_new_deck') == 'true'
        new_deck_name = request.POST.get('new_deck_name', '')

        if not uploaded_file:
            return JsonResponse({'error': 'Aucun fichier uploadé'}, status=400)

        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            mime_type = uploaded_file.content_type or 'application/octet-stream'

        # Déterminer le type de document
        if 'pdf' in mime_type:
            doc_type = 'pdf'
        elif 'image' in mime_type:
            doc_type = 'image'
        elif 'text' in mime_type:
            doc_type = 'text'
        else:
            doc_type = 'other'

        # Créer l'entrée DocumentUpload
        document = DocumentUpload.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            document_type=doc_type,
            mime_type=mime_type,
            status='pending',
        )

        # Marquer comme en traitement
        document.mark_as_processing()

        try:
            # Extraire le texte du document
            file_path = document.file.path
            extracted_text, extraction_method = extract_text_from_file(file_path, mime_type)

            document.extracted_text = extracted_text
            document.text_extraction_method = extraction_method
            document.save(update_fields=['extracted_text', 'text_extraction_method'])

            # Prétraiter le texte
            clean_text = preprocess_text_for_flashcards(extracted_text, max_length=8000)

            # Détection de langue
            detected_lang = detect_document_language(clean_text)

            # Déterminer la langue pour le générateur
            generator_language = 'french' if detected_lang in ['fr', 'fra'] else 'english'

            # Générer les flashcards avec les bibliothèques open-source
            generator = FlashcardGeneratorService(language=generator_language)
            flashcards_data = generator.generate_flashcards(
                text=clean_text,
                max_cards=max_cards,
                difficulty_levels=True,
                language=detected_lang
            )

            # Déterminer le deck cible
            target_deck = None
            if create_new_deck and new_deck_name:
                # Créer un nouveau deck
                target_deck = FlashcardDeck.objects.create(
                    user=request.user,
                    name=new_deck_name,
                    description=f"Généré automatiquement depuis: {uploaded_file.name}"
                )
            elif deck_id:
                # Utiliser un deck existant
                target_deck = get_object_or_404(
                    FlashcardDeck,
                    id=deck_id,
                    user=request.user
                )

            # Créer les flashcards dans la base
            created_cards = []
            if target_deck:
                for card_data in flashcards_data:
                    flashcard = Flashcard.objects.create(
                        user=request.user,
                        deck=target_deck,
                        front_text=card_data['question'],
                        back_text=card_data['answer'],
                        front_language=detected_lang or '',
                        back_language=detected_lang or '',
                    )
                    created_cards.append(flashcard)

                # Mettre à jour le document
                document.deck = target_deck

            # Marquer comme complété
            document.mark_as_completed(flashcards_count=len(flashcards_data))

            # Sauvegarder les paramètres de génération
            document.generation_params = {
                'max_cards': max_cards,
                'generator': 'scikit-learn + spaCy',
                'detected_language': detected_lang,
                'extraction_method': extraction_method,
                'language': generator_language,
            }
            document.save(update_fields=['deck', 'generation_params'])

            # Réponse pour HTMX
            context = {
                'flashcards': flashcards_data,
                'deck': target_deck,
                'document': document,
                'success': True,
            }

            return render(request, 'ai_documents/partials/flashcards_list.html', context)

        except Exception as e:
            # Erreur lors du traitement
            document.mark_as_failed(error_message=str(e))
            return JsonResponse({
                'error': f'Erreur lors du traitement: {str(e)}',
                'success': False
            }, status=500)

    except Exception as e:
        return JsonResponse({
            'error': f'Erreur: {str(e)}',
            'success': False
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_upload_status(request, upload_id):
    """
    Récupère le statut d'un upload en cours

    Args:
        upload_id: ID du DocumentUpload

    Returns:
        JSON avec le statut
    """
    document = get_object_or_404(
        DocumentUpload,
        id=upload_id,
        user=request.user
    )

    return JsonResponse({
        'status': document.status,
        'progress': {
            'pending': document.status == 'pending',
            'processing': document.status == 'processing',
            'completed': document.status == 'completed',
            'failed': document.status == 'failed',
        },
        'error_message': document.error_message if document.status == 'failed' else None,
        'flashcards_count': document.flashcards_generated_count,
        'extraction_method': document.text_extraction_method,
    })
