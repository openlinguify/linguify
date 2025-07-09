# backend/apps/revision/tests/test_learning_viewsets.py

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from apps.revision.models import FlashcardDeck, Flashcard
from apps.revision.views.flashcard_views import FlashcardDeckViewSet, FlashcardViewSet

User = get_user_model()


class LearningSettingsViewSetTest(APITestCase):
    """Tests détaillés pour les ViewSets avec paramètres d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name='ViewSet Test Deck',
            description='Test deck for ViewSet testing',
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        self.other_deck = FlashcardDeck.objects.create(
            user=self.other_user,
            name='Other User Deck',
            required_reviews_to_learn=5
        )
        
        self.card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='ViewSet test card',
            back_text='ViewSet test answer'
        )

    def test_learning_settings_get_authenticated(self):
        """Test GET learning_settings avec utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier la structure de la réponse
        expected_fields = [
            'id', 'name', 'required_reviews_to_learn', 
            'auto_mark_learned', 'reset_on_wrong_answer',
            'learning_statistics', 'learning_presets'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Vérifier les valeurs
        self.assertEqual(data['required_reviews_to_learn'], 3)
        self.assertTrue(data['auto_mark_learned'])
        self.assertFalse(data['reset_on_wrong_answer'])

    def test_learning_settings_get_unauthenticated(self):
        """Test GET learning_settings sans authentification"""
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_learning_settings_get_unauthorized(self):
        """Test GET learning_settings par un autre utilisateur"""
        self.client.force_authenticate(user=self.other_user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_learning_settings_patch_success(self):
        """Test PATCH learning_settings avec succès"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        data = {
            'required_reviews_to_learn': 7,
            'auto_mark_learned': False,
            'reset_on_wrong_answer': True
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les changements sont persistés
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.required_reviews_to_learn, 7)
        self.assertFalse(self.deck.auto_mark_learned)
        self.assertTrue(self.deck.reset_on_wrong_answer)

    def test_learning_settings_patch_partial(self):
        """Test PATCH partiel learning_settings"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        data = {
            'required_reviews_to_learn': 10
            # Seulement un champ
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que seul le champ modifié a changé
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.required_reviews_to_learn, 10)
        self.assertTrue(self.deck.auto_mark_learned)  # Inchangé
        self.assertFalse(self.deck.reset_on_wrong_answer)  # Inchangé

    @patch('apps.revision.models.FlashcardDeck.recalculate_cards_learned_status')
    def test_learning_settings_patch_triggers_recalculation(self, mock_recalculate):
        """Test que PATCH déclenche le recalcul des statuts"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        data = {
            'required_reviews_to_learn': 5  # Changement
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifier que le recalcul a été appelé
        mock_recalculate.assert_called_once()

    def test_apply_preset_success(self):
        """Test apply_preset avec succès"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        data = {'preset_name': 'intensive'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le preset a été appliqué
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.required_reviews_to_learn, 5)
        self.assertTrue(self.deck.auto_mark_learned)
        self.assertTrue(self.deck.reset_on_wrong_answer)  # Le preset "intensive" a reset=True

    def test_apply_preset_invalid(self):
        """Test apply_preset avec preset invalide"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        data = {'preset_name': 'invalid_preset'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_card_progress_success(self):
        """Test update_review_progress avec succès"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier la structure de la réponse
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('card', response_data)
        self.assertIn('learning_progress', response_data)
        
        # Vérifier les données de progression
        progress = response_data['learning_progress']
        self.assertEqual(progress['correct_reviews'], 1)
        self.assertEqual(progress['total_reviews'], 1)
        self.assertFalse(progress['is_learned'])

    def test_update_card_progress_multiple_times(self):
        """Test update_review_progress plusieurs fois jusqu'à apprentissage"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        
        # 3 révisions correctes (required_reviews_to_learn = 3)
        for i in range(3):
            response = self.client.post(url, {'is_correct': True}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            progress = response.json()['learning_progress']
            self.assertEqual(progress['correct_reviews'], i + 1)
            self.assertEqual(progress['total_reviews'], i + 1)
            
            if i < 2:  # Pas encore apprise
                self.assertFalse(progress['is_learned'])
            else:  # Maintenant apprise
                self.assertTrue(progress['is_learned'])

    def test_update_card_progress_incorrect_answer(self):
        """Test update_review_progress avec réponse incorrecte"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': False}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        progress = response.json()['learning_progress']
        self.assertEqual(progress['correct_reviews'], 0)
        self.assertEqual(progress['total_reviews'], 1)
        self.assertFalse(progress['is_learned'])

    def test_update_card_progress_unauthorized(self):
        """Test update_review_progress par un autre utilisateur"""
        self.client.force_authenticate(user=self.other_user)
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_card_progress_archived_deck(self):
        """Test update_review_progress sur deck archivé"""
        self.client.force_authenticate(user=self.user)
        
        # Archiver le deck
        self.deck.is_archived = True
        self.deck.save()
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('archived', response.data['detail'].lower())

    @patch('apps.revision.models.Flashcard.update_review_progress')
    def test_update_card_progress_model_exception(self, mock_update):
        """Test gestion d'exception dans update_review_progress"""
        self.client.force_authenticate(user=self.user)
        
        # Simuler une exception dans le modèle
        mock_update.side_effect = Exception("Database error")
        
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Failed to update review progress', response.data['detail'])

    def test_learning_settings_get_includes_statistics(self):
        """Test que GET learning_settings inclut les statistiques"""
        self.client.force_authenticate(user=self.user)
        
        # Créer quelques cartes avec différents états
        for i in range(5):
            card = Flashcard.objects.create(
                user=self.user,
                deck=self.deck,
                front_text=f'Stats card {i+1}',
                back_text=f'Stats answer {i+1}',
                correct_reviews_count=i % 3,
                total_reviews_count=i % 3 + 1,
                learned=(i % 3) >= 2
            )
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        stats = data['learning_statistics']
        
        # Vérifier la structure des statistiques
        self.assertIn('total_cards', stats)
        self.assertIn('learned_cards', stats)
        self.assertIn('average_progress', stats)
        self.assertIn('cards_needing_review', stats)
        
        # Vérifier les valeurs (6 cartes total: 1 original + 5 créées)
        self.assertEqual(stats['total_cards'], 6)

    def test_learning_settings_get_includes_presets(self):
        """Test que GET learning_settings inclut les presets"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        presets = data['learning_presets']
        
        # Vérifier que tous les presets sont présents
        expected_presets = ['beginner', 'normal', 'intensive', 'expert']
        for preset_name in expected_presets:
            self.assertIn(preset_name, presets)
            
            # Vérifier la structure de chaque preset
            preset = presets[preset_name]
            self.assertIn('name', preset)
            self.assertIn('description', preset)
            self.assertIn('required_reviews_to_learn', preset)
            self.assertIn('auto_mark_learned', preset)
            self.assertIn('reset_on_wrong_answer', preset)

    def test_method_not_allowed(self):
        """Test méthodes HTTP non autorisées"""
        self.client.force_authenticate(user=self.user)
        
        # Test PUT sur learning_settings (seuls GET et PATCH autorisés)
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Test GET sur apply_preset (seul POST autorisé)
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_content_type_validation(self):
        """Test validation du Content-Type"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        
        # Envoyer des données avec mauvais Content-Type
        response = self.client.patch(
            url,
            data='required_reviews_to_learn=5',
            content_type='application/x-www-form-urlencoded'
        )
        
        # Devrait fonctionner quand même (DRF gère plusieurs formats)
        self.assertIn(response.status_code, [200, 400])

    @patch('apps.revision.models.FlashcardDeck.objects.get')
    def test_deck_not_found_handling(self, mock_get):
        """Test gestion du deck non trouvé"""
        self.client.force_authenticate(user=self.user)
        
        # Simuler un deck non trouvé
        from django.core.exceptions import ObjectDoesNotExist
        mock_get.side_effect = ObjectDoesNotExist("Deck not found")
        
        url = reverse('revision:deck-learning-settings', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_request_body_handling(self):
        """Test gestion des requêtes avec corps vide"""
        self.client.force_authenticate(user=self.user)
        
        # PATCH avec corps vide
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.patch(url, {}, format='json')
        
        # Devrait réussir (pas de changement)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # POST avec corps vide sur apply_preset
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        response = self.client.post(url, {}, format='json')
        
        # Devrait échouer (preset_name requis)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LearningSettingsViewSetMockTest(TestCase):
    """Tests avec mocks pour tester l'isolation des composants"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='mockuser',
            email='mock@example.com',
            password='mockpass123'
        )

    @patch('apps.revision.serializers.DeckLearningSettingsSerializer')
    def test_learning_settings_serializer_integration(self, mock_serializer_class):
        """Test intégration avec le serializer"""
        from rest_framework.test import APIRequestFactory
        from apps.revision.views.flashcard_views import FlashcardDeckViewSet
        
        # Configurer le mock
        mock_serializer = MagicMock()
        mock_serializer.data = {
            'required_reviews_to_learn': 3,
            'auto_mark_learned': True,
            'reset_on_wrong_answer': False
        }
        mock_serializer_class.return_value = mock_serializer
        
        # Créer une requête mock
        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.user = self.user
        
        # Créer un deck mock
        deck_mock = MagicMock()
        deck_mock.user = self.user
        
        # Créer et tester la vue
        view = FlashcardDeckViewSet()
        view.request = request
        view.get_object = MagicMock(return_value=deck_mock)
        
        response = view.learning_settings(request, pk=1)
        
        # Vérifier que le serializer a été appelé correctement
        mock_serializer_class.assert_called_once_with(deck_mock, context={'request': request})
        self.assertEqual(response.status_code, 200)

    @patch('apps.revision.models.Flashcard.update_review_progress')
    def test_card_progress_model_integration(self, mock_update_progress):
        """Test intégration avec le modèle de carte"""
        from rest_framework.test import APIRequestFactory
        from apps.revision.views.flashcard_views import FlashcardViewSet
        
        # Créer une carte mock
        card_mock = MagicMock()
        card_mock.user = self.user
        card_mock.deck.is_archived = False
        card_mock.id = 1
        
        # Configurer le mock de mise à jour
        mock_update_progress.return_value = None
        
        # Créer une requête mock
        factory = APIRequestFactory()
        request = factory.post('/test/', {'is_correct': True}, format='json')
        request.user = self.user
        request.data = {'is_correct': True}
        
        # Créer et tester la vue
        view = FlashcardViewSet()
        view.request = request
        view.get_object = MagicMock(return_value=card_mock)
        view.get_serializer = MagicMock(return_value=MagicMock(data={}))
        
        response = view.update_review_progress(request, pk=1)
        
        # Vérifier que la méthode du modèle a été appelée
        mock_update_progress.assert_called_once_with(is_correct=True)
        self.assertEqual(response.status_code, 200)

    @patch('apps.revision.models.FlashcardDeck.get_learning_statistics')
    @patch('apps.revision.models.FlashcardDeck.get_learning_presets')
    def test_statistics_and_presets_calls(self, mock_presets, mock_stats):
        """Test appels aux méthodes de statistiques et presets"""
        from rest_framework.test import APIRequestFactory
        from apps.revision.views.flashcard_views import FlashcardDeckViewSet
        
        # Configurer les mocks
        mock_stats.return_value = {'total_cards': 5, 'learned_cards': 2}
        mock_presets.return_value = {'normal': {'name': 'Normal'}}
        
        # Créer un deck mock
        deck_mock = MagicMock()
        deck_mock.user = self.user
        deck_mock.id = 1
        deck_mock.name = 'Test Deck'
        deck_mock.required_reviews_to_learn = 3
        deck_mock.auto_mark_learned = True
        deck_mock.reset_on_wrong_answer = False
        
        # Créer une requête mock
        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.user = self.user
        
        # Créer et tester la vue
        view = FlashcardDeckViewSet()
        view.request = request
        view.get_object = MagicMock(return_value=deck_mock)
        
        response = view.learning_settings(request, pk=1)
        
        # Vérifier que les méthodes ont été appelées
        mock_stats.assert_called_once()
        mock_presets.assert_called_once()
        self.assertEqual(response.status_code, 200)