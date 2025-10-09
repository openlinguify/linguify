"""
Vues pour l'import de documents (PDF, images) et génération de flashcards
Intégration avec l'app ai_documents
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.revision.models import FlashcardDeck, Flashcard, DocumentUpload
from apps.ai_documents.utils.text_extraction import extract_text_from_file, preprocess_text_for_flashcards, detect_document_language
from apps.ai_documents.services import FlashcardGeneratorService

import mimetypes
import logging

logger = logging.getLogger(__name__)


class DocumentImportAPIView(APIView):
    """
    API pour importer un document et générer des flashcards automatiquement
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id):
        """
        Traite un document uploadé et génère des flashcards dans un deck existant

        Args:
            deck_id: ID du deck cible
        """
        try:
            # Récupérer le fichier et paramètres
            uploaded_file = request.FILES.get('document')
            max_cards = int(request.data.get('max_cards', 10))

            if not uploaded_file:
                return Response(
                    {'error': 'Aucun fichier uploadé'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Vérifier que le deck existe et appartient à l'utilisateur
            deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)

            # Vérifier que le deck n'est pas archivé
            if deck.is_archived:
                return Response(
                    {'error': 'Impossible d\'importer dans un deck archivé'},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                return Response(
                    {'error': f'Type de fichier non supporté: {mime_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Créer l'entrée DocumentUpload
            document = DocumentUpload.objects.create(
                user=request.user,
                deck=deck,
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
                generator_language = 'french' if detected_lang in ['fr', 'fra'] else 'english'

                # Générer les flashcards avec NLP open-source
                generator = FlashcardGeneratorService(language=generator_language)
                flashcards_data = generator.generate_flashcards(
                    text=clean_text,
                    max_cards=max_cards,
                    difficulty_levels=True,
                    language=detected_lang
                )

                # Créer les flashcards dans le deck
                created_cards = []
                for card_data in flashcards_data:
                    flashcard = Flashcard.objects.create(
                        user=request.user,
                        deck=deck,
                        front_text=card_data['question'],
                        back_text=card_data['answer'],
                        front_language=detected_lang or '',
                        back_language=detected_lang or '',
                    )
                    created_cards.append({
                        'id': flashcard.id,
                        'front_text': flashcard.front_text,
                        'back_text': flashcard.back_text,
                        'difficulty': card_data.get('difficulty', 'medium'),
                        'relevance_score': card_data.get('relevance_score', 0.5),
                    })

                # Marquer comme complété
                document.mark_as_completed(flashcards_count=len(flashcards_data))

                # Sauvegarder les paramètres
                document.generation_params = {
                    'max_cards': max_cards,
                    'generator': 'scikit-learn + spaCy',
                    'detected_language': detected_lang,
                    'extraction_method': extraction_method,
                    'language': generator_language,
                }
                document.save(update_fields=['generation_params'])

                return Response({
                    'success': True,
                    'message': f'{len(created_cards)} flashcards générées avec succès',
                    'cards_created': len(created_cards),
                    'deck_id': deck.id,
                    'deck_name': deck.name,
                    'preview': created_cards[:5],  # Aperçu des 5 premières
                    'extraction_method': extraction_method,
                    'detected_language': detected_lang,
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Erreur lors du traitement
                logger.error(f"Error processing document: {str(e)}")
                document.mark_as_failed(error_message=str(e))
                return Response({
                    'error': f'Erreur lors du traitement: {str(e)}',
                    'success': False
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error in document import: {str(e)}")
            return Response({
                'error': f'Erreur: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
