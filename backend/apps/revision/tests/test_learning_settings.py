# backend/apps/revision/tests/test_learning_settings.py

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.revision.models import FlashcardDeck, Flashcard

User = get_user_model()


class LearningSettingsModelTest(TestCase):
    """Tests pour les modèles avec paramètres d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Test Deck',
            description='Test deck for learning settings',
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        self.card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Test question',
            back_text='Test answer'
        )

    def test_deck_default_learning_settings(self):
        """Test des paramètres par défaut du deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Default Deck'
        )
        
        self.assertEqual(deck.required_reviews_to_learn, 3)
        self.assertTrue(deck.auto_mark_learned)
        self.assertFalse(deck.reset_on_wrong_answer)

    def test_card_default_progress_fields(self):
        """Test des champs de progression par défaut de la carte"""
        self.assertEqual(self.card.correct_reviews_count, 0)
        self.assertEqual(self.card.total_reviews_count, 0)
        self.assertFalse(self.card.learned)

    def test_learning_progress_percentage(self):
        """Test du calcul du pourcentage de progression"""
        # Progression initiale
        self.assertEqual(self.card.learning_progress_percentage, 0)
        
        # Après 1 révision correcte sur 3 requises
        self.card.correct_reviews_count = 1
        self.card.save()
        self.assertAlmostEqual(self.card.learning_progress_percentage, 33.33, places=1)
        
        # Après 2 révisions correctes
        self.card.correct_reviews_count = 2
        self.card.save()
        self.assertAlmostEqual(self.card.learning_progress_percentage, 66.67, places=1)
        
        # Carte apprise
        self.card.learned = True
        self.card.save()
        self.assertEqual(self.card.learning_progress_percentage, 100)

    def test_reviews_remaining_to_learn(self):
        """Test du calcul des révisions restantes"""
        # Début: 3 révisions restantes
        self.assertEqual(self.card.reviews_remaining_to_learn, 3)
        
        # Après 1 révision correcte
        self.card.correct_reviews_count = 1
        self.card.save()
        self.assertEqual(self.card.reviews_remaining_to_learn, 2)
        
        # Après 3 révisions correctes
        self.card.correct_reviews_count = 3
        self.card.save()
        self.assertEqual(self.card.reviews_remaining_to_learn, 0)
        
        # Carte apprise
        self.card.learned = True
        self.card.save()
        self.assertEqual(self.card.reviews_remaining_to_learn, 0)

    def test_update_review_progress_correct(self):
        """Test de mise à jour du progrès avec réponse correcte"""
        initial_time = self.card.last_reviewed
        
        self.card.update_review_progress(is_correct=True)
        
        # Vérifier les compteurs
        self.assertEqual(self.card.correct_reviews_count, 1)
        self.assertEqual(self.card.total_reviews_count, 1)
        self.assertEqual(self.card.review_count, 1)
        self.assertNotEqual(self.card.last_reviewed, initial_time)
        self.assertFalse(self.card.learned)  # Pas encore apprise (1/3)

    def test_update_review_progress_incorrect(self):
        """Test de mise à jour du progrès avec réponse incorrecte"""
        self.card.update_review_progress(is_correct=False)
        
        # Vérifier les compteurs
        self.assertEqual(self.card.correct_reviews_count, 0)
        self.assertEqual(self.card.total_reviews_count, 1)
        self.assertEqual(self.card.review_count, 1)
        self.assertFalse(self.card.learned)

    def test_auto_mark_learned(self):
        """Test du marquage automatique comme apprise"""
        # 3 révisions correctes avec auto_mark_learned=True
        for i in range(3):
            self.card.update_review_progress(is_correct=True)
        
        self.assertTrue(self.card.learned)
        self.assertEqual(self.card.correct_reviews_count, 3)

    def test_auto_mark_learned_disabled(self):
        """Test avec marquage automatique désactivé"""
        self.deck.auto_mark_learned = False
        self.deck.save()
        
        # 3 révisions correctes avec auto_mark_learned=False
        for i in range(3):
            self.card.update_review_progress(is_correct=True)
        
        self.assertFalse(self.card.learned)  # Pas marquée automatiquement
        self.assertEqual(self.card.correct_reviews_count, 3)

    def test_reset_on_wrong_answer(self):
        """Test du reset du compteur sur mauvaise réponse"""
        # Configuration avec reset activé
        self.deck.reset_on_wrong_answer = True
        self.deck.save()
        
        # 2 révisions correctes
        for i in range(2):
            self.card.update_review_progress(is_correct=True)
        self.assertEqual(self.card.correct_reviews_count, 2)
        
        # 1 révision incorrecte -> reset
        self.card.update_review_progress(is_correct=False)
        self.assertEqual(self.card.correct_reviews_count, 0)
        self.assertEqual(self.card.total_reviews_count, 3)
        self.assertFalse(self.card.learned)

    def test_learning_statistics(self):
        """Test des statistiques d'apprentissage du deck"""
        # Créer plusieurs cartes avec différents états
        Flashcard.objects.create(
            user=self.user, deck=self.deck,
            front_text='Card 2', back_text='Answer 2',
            learned=True, correct_reviews_count=3, total_reviews_count=3
        )
        
        Flashcard.objects.create(
            user=self.user, deck=self.deck,
            front_text='Card 3', back_text='Answer 3',
            correct_reviews_count=1, total_reviews_count=2
        )
        
        stats = self.deck.get_learning_statistics()
        
        self.assertEqual(stats['total_cards'], 3)
        self.assertEqual(stats['learned_cards'], 1)
        self.assertEqual(stats['cards_needing_review'], 2)
        self.assertIsInstance(stats['average_progress'], (int, float))

    def test_learning_presets(self):
        """Test des presets de configuration"""
        presets = self.deck.get_learning_presets()
        
        self.assertIn('beginner', presets)
        self.assertIn('normal', presets)
        self.assertIn('intensive', presets)
        self.assertIn('expert', presets)
        
        # Vérifier la structure d'un preset
        beginner = presets['beginner']
        self.assertIn('name', beginner)
        self.assertIn('description', beginner)
        self.assertIn('required_reviews_to_learn', beginner)
        self.assertIn('auto_mark_learned', beginner)
        self.assertIn('reset_on_wrong_answer', beginner)

    def test_recalculate_cards_learned_status(self):
        """Test du recalcul du statut des cartes"""
        # Marquer une carte comme apprise manuellement
        self.card.learned = True
        self.card.correct_reviews_count = 1  # Moins que requis
        self.card.save()
        
        # Recalculer selon les nouveaux paramètres
        self.deck.recalculate_cards_learned_status()
        
        # Recharger la carte
        self.card.refresh_from_db()
        
        # La carte ne devrait plus être apprise car < 3 révisions
        self.assertFalse(self.card.learned)


class LearningSettingsAPITest(APITestCase):
    """Tests pour l'API des paramètres d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Test Deck',
            description='Test deck for API',
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        self.card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Test question',
            back_text='Test answer'
        )
        
        self.client.force_authenticate(user=self.user)

    def test_get_learning_settings(self):
        """Test GET /api/v1/revision/decks/{id}/learning_settings/"""
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['required_reviews_to_learn'], 3)
        self.assertTrue(data['auto_mark_learned'])
        self.assertFalse(data['reset_on_wrong_answer'])
        self.assertIn('learning_statistics', data)
        self.assertIn('learning_presets', data)

    def test_update_learning_settings(self):
        """Test PATCH /api/v1/revision/decks/{id}/learning_settings/"""
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        data = {
            'required_reviews_to_learn': 5,
            'auto_mark_learned': False,
            'reset_on_wrong_answer': True
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que les paramètres ont été mis à jour
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.required_reviews_to_learn, 5)
        self.assertFalse(self.deck.auto_mark_learned)
        self.assertTrue(self.deck.reset_on_wrong_answer)

    def test_update_learning_settings_invalid_values(self):
        """Test avec des valeurs invalides"""
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        data = {
            'required_reviews_to_learn': 25,  # > 20, invalide
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_apply_preset(self):
        """Test POST /api/v1/revision/decks/{id}/apply_preset/"""
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        data = {'preset_name': 'intensive'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le preset a été appliqué
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.required_reviews_to_learn, 5)
        self.assertTrue(self.deck.auto_mark_learned)
        self.assertTrue(self.deck.reset_on_wrong_answer)  # Le preset "intensive" a reset=True

    def test_apply_invalid_preset(self):
        """Test avec un preset invalide"""
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        data = {'preset_name': 'invalid_preset'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_card_progress(self):
        """Test POST /api/v1/revision/flashcards/{id}/update_review_progress/"""
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        data = {'is_correct': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('learning_progress', data)
        self.assertEqual(data['learning_progress']['correct_reviews'], 1)
        self.assertEqual(data['learning_progress']['total_reviews'], 1)
        self.assertFalse(data['learning_progress']['is_learned'])

    def test_update_card_progress_until_learned(self):
        """Test progression jusqu'à ce que la carte soit apprise"""
        url = reverse('revision:flashcard-update-review-progress', args=[self.card.id])
        
        # 3 révisions correctes
        for i in range(3):
            response = self.client.post(url, {'is_correct': True}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertTrue(data['learning_progress']['is_learned'])
        self.assertEqual(data['learning_progress']['correct_reviews'], 3)

    def test_unauthorized_access(self):
        """Test accès non autorisé"""
        # Créer un autre utilisateur
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        # Essayer d'accéder aux paramètres du deck d'un autre utilisateur
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        # Peut retourner 403 (forbidden) ou 404 (not found) selon l'implémentation
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_learning_settings_permissions(self):
        """Test des permissions pour les paramètres d'apprentissage"""
        # Test sans authentification
        self.client.force_authenticate(user=None)
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        response = self.client.get(url)
        
        # Peut retourner 401 ou 403 selon la configuration de DRF
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class LearningSettingsSerializerTest(TestCase):
    """Tests pour les serializers des paramètres d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Test Deck'
        )

    def test_flashcard_serializer_new_fields(self):
        """Test des nouveaux champs dans FlashcardSerializer"""
        from apps.revision.serializers import FlashcardSerializer
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Test',
            back_text='Answer',
            correct_reviews_count=2,
            total_reviews_count=3
        )
        
        serializer = FlashcardSerializer(card)
        data = serializer.data
        
        self.assertIn('correct_reviews_count', data)
        self.assertIn('total_reviews_count', data)
        self.assertIn('learning_progress_percentage', data)
        self.assertIn('reviews_remaining_to_learn', data)
        
        self.assertEqual(data['correct_reviews_count'], 2)
        self.assertEqual(data['total_reviews_count'], 3)

    def test_deck_serializer_learning_fields(self):
        """Test des champs d'apprentissage dans FlashcardDeckSerializer"""
        from apps.revision.serializers import FlashcardDeckSerializer
        
        serializer = FlashcardDeckSerializer(self.deck)
        data = serializer.data
        
        self.assertIn('required_reviews_to_learn', data)
        self.assertIn('auto_mark_learned', data)
        self.assertIn('reset_on_wrong_answer', data)
        self.assertIn('learning_statistics', data)
        self.assertIn('learning_presets', data)

    def test_learning_settings_serializer_validation(self):
        """Test de validation du DeckLearningSettingsSerializer"""
        from apps.revision.serializers import DeckLearningSettingsSerializer
        
        # Données valides
        valid_data = {
            'required_reviews_to_learn': 5,
            'auto_mark_learned': True,
            'reset_on_wrong_answer': False
        }
        
        serializer = DeckLearningSettingsSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Données invalides - trop de révisions
        invalid_data = {
            'required_reviews_to_learn': 25,  # > 20
        }
        
        serializer = DeckLearningSettingsSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('required_reviews_to_learn', serializer.errors)