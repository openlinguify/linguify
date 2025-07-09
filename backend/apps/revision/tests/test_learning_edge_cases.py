# backend/apps/revision/tests/test_learning_edge_cases.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from apps.revision.models import FlashcardDeck, Flashcard
from apps.revision.serializers import DeckLearningSettingsSerializer, ApplyPresetSerializer

User = get_user_model()


class LearningSettingsEdgeCasesTest(TestCase):
    """Tests pour les cas limites et situations d'erreur"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_minimal_required_reviews_edge_case(self):
        """Test avec 1 révision requise (cas limite minimal)"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Minimal Reviews Deck',
            required_reviews_to_learn=1  # Cas limite minimal
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Minimal reviews card',
            back_text='Minimal reviews answer'
        )
        
        # Avec 1 révision requise, progression initiale devrait être 0%
        self.assertEqual(card.learning_progress_percentage, 0)
        self.assertEqual(card.reviews_remaining_to_learn, 1)
        
        # Une révision correcte devrait marquer comme apprise
        card.update_review_progress(is_correct=True)
        self.assertTrue(card.learned)
        self.assertEqual(card.learning_progress_percentage, 100)

    def test_very_high_required_reviews(self):
        """Test avec un nombre très élevé de révisions requises"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='High Reviews Deck',
            required_reviews_to_learn=50  # Très élevé
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='High reviews card',
            back_text='High reviews answer'
        )
        
        # Après 10 révisions correctes
        for _ in range(10):
            card.update_review_progress(is_correct=True)
        
        self.assertEqual(card.correct_reviews_count, 10)
        self.assertFalse(card.learned)
        self.assertEqual(card.learning_progress_percentage, 20)  # 10/50 * 100
        self.assertEqual(card.reviews_remaining_to_learn, 40)

    def test_already_learned_card_behavior(self):
        """Test comportement d'une carte déjà marquée comme apprise"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Already Learned Deck',
            required_reviews_to_learn=5,
            reset_on_wrong_answer=True
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Already learned card',
            back_text='Already learned answer',
            learned=True,  # Déjà apprise
            correct_reviews_count=5
        )
        
        # Progression d'une carte déjà apprise
        self.assertEqual(card.learning_progress_percentage, 100)
        self.assertEqual(card.reviews_remaining_to_learn, 0)
        
        # Erreur sur une carte apprise avec reset activé
        card.update_review_progress(is_correct=False)
        
        # Devrait réinitialiser même si déjà apprise
        self.assertFalse(card.learned)
        self.assertEqual(card.correct_reviews_count, 0)

    def test_concurrent_updates_safety(self):
        """Test sécurité des mises à jour concurrentes"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Concurrent Updates Deck',
            required_reviews_to_learn=3
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Concurrent card',
            back_text='Concurrent answer'
        )
        
        # Simuler des mises à jour séquentielles
        # (Django ne gère pas vraiment la concurrence dans les tests)
        
        # Première mise à jour
        card.update_review_progress(is_correct=True)
        
        # Recharger et faire une deuxième mise à jour
        card.refresh_from_db()
        card.update_review_progress(is_correct=True)
        
        # Recharger la carte finale
        card.refresh_from_db()
        
        # Devrait avoir 2 révisions
        self.assertEqual(card.total_reviews_count, 2)
        self.assertEqual(card.correct_reviews_count, 2)

    def test_invalid_progress_data_recovery(self):
        """Test récupération après données invalides"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Invalid Data Deck',
            required_reviews_to_learn=3
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Invalid data card',
            back_text='Invalid data answer'
        )
        
        # Test avec des données limite (pas des violations de contraintes)
        # Tester avec correct_reviews > required_reviews (cas limite valide)
        card.correct_reviews_count = 10  # Plus que requis
        card.total_reviews_count = 12    # Cohérent
        card.save()
        
        # Les propriétés calculées devraient gérer gracieusement
        try:
            progress = card.learning_progress_percentage
            remaining = card.reviews_remaining_to_learn
            
            # Ne devrait pas lever d'exception
            self.assertIsInstance(progress, (int, float))
            self.assertIsInstance(remaining, int)
            
            # Les valeurs devraient être sensées
            self.assertGreaterEqual(progress, 0)
            self.assertLessEqual(progress, 100)
            self.assertGreaterEqual(remaining, 0)
            
            # Avec 10 révisions correctes sur 3 requises, progression = 100%
            self.assertEqual(progress, 100)
            self.assertEqual(remaining, 0)
            
        except Exception as e:
            self.fail(f"Exception levée avec données limite: {e}")

    def test_deck_deletion_cascade(self):
        """Test suppression en cascade du deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Deletion Test Deck',
            required_reviews_to_learn=3
        )
        
        cards = []
        for i in range(5):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Card {i+1}',
                back_text=f'Answer {i+1}'
            )
            card.update_review_progress(is_correct=True)
            cards.append(card)
        
        # Vérifier que les cartes existent
        self.assertEqual(Flashcard.objects.filter(deck=deck).count(), 5)
        
        # Supprimer le deck
        deck_id = deck.id
        deck.delete()
        
        # Les cartes devraient être supprimées en cascade
        self.assertEqual(Flashcard.objects.filter(deck_id=deck_id).count(), 0)

    def test_user_deletion_impact(self):
        """Test impact de la suppression d'utilisateur"""
        # Créer un autre utilisateur temporaire
        temp_user = User.objects.create_user(
            username='tempuser',
            email='temp@example.com',
            password='temppass123'
        )
        
        deck = FlashcardDeck.objects.create(
            user=temp_user,
            name='Temp User Deck',
            required_reviews_to_learn=3
        )
        
        card = Flashcard.objects.create(
            user=temp_user,
            deck=deck,
            front_text='Temp card',
            back_text='Temp answer'
        )
        
        card.update_review_progress(is_correct=True)
        
        deck_id = deck.id
        card_id = card.id
        
        # Supprimer l'utilisateur
        temp_user.delete()
        
        # Les decks et cartes devraient être supprimés
        self.assertFalse(FlashcardDeck.objects.filter(id=deck_id).exists())
        self.assertFalse(Flashcard.objects.filter(id=card_id).exists())

    def test_extreme_values_handling(self):
        """Test gestion des valeurs extrêmes"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Extreme Values Deck',
            required_reviews_to_learn=1000  # Très élevé
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Extreme card',
            back_text='Extreme answer'
        )
        
        # Mettre à jour un grand nombre de fois
        for _ in range(500):
            card.update_review_progress(is_correct=True)
        
        # Vérifier que les calculs restent cohérents
        self.assertEqual(card.correct_reviews_count, 500)
        self.assertEqual(card.total_reviews_count, 500)
        self.assertEqual(card.learning_progress_percentage, 50)  # 500/1000 * 100
        self.assertEqual(card.reviews_remaining_to_learn, 500)
        self.assertFalse(card.learned)

    def test_mixed_settings_interactions(self):
        """Test interactions complexes entre paramètres"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Mixed Settings Deck',
            required_reviews_to_learn=3,
            auto_mark_learned=False,  # Pas de marquage auto
            reset_on_wrong_answer=True  # Mais reset activé
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Mixed settings card',
            back_text='Mixed settings answer'
        )
        
        # 3 révisions correctes
        for _ in range(3):
            card.update_review_progress(is_correct=True)
        
        # Pas apprise automatiquement
        self.assertFalse(card.learned)
        self.assertEqual(card.correct_reviews_count, 3)
        
        # Marquage manuel
        card.learned = True
        card.save()
        self.assertTrue(card.learned)
        
        # Erreur -> reset mais pas de changement auto du learned
        card.update_review_progress(is_correct=False)
        
        # Reset du compteur mais learned reste True (pas de marquage auto)
        self.assertEqual(card.correct_reviews_count, 0)
        self.assertFalse(card.learned)  # Reset force à False

    def test_presets_boundary_values(self):
        """Test valeurs limites des presets"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Presets Test Deck'
        )
        
        presets = deck.get_learning_presets()
        
        # Vérifier que tous les presets ont des valeurs valides
        for preset_name, preset_data in presets.items():
            self.assertGreaterEqual(
                preset_data['required_reviews_to_learn'], 1,
                f"Preset {preset_name} has invalid required_reviews"
            )
            self.assertLessEqual(
                preset_data['required_reviews_to_learn'], 20,
                f"Preset {preset_name} has too high required_reviews"
            )
            self.assertIsInstance(
                preset_data['auto_mark_learned'], bool,
                f"Preset {preset_name} has invalid auto_mark_learned"
            )
            self.assertIsInstance(
                preset_data['reset_on_wrong_answer'], bool,
                f"Preset {preset_name} has invalid reset_on_wrong_answer"
            )


class LearningSettingsAPIEdgeCasesTest(APITestCase):
    """Tests API pour les cas d'erreur et limites"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name='API Test Deck'
        )
        
        self.client.force_authenticate(user=self.user)

    def test_invalid_deck_id(self):
        """Test avec ID de deck invalide"""
        from django.urls import reverse
        
        # ID inexistant
        url = reverse('revision:deck-learning-settings', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_malformed_request_data(self):
        """Test avec données malformées"""
        from django.urls import reverse
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        
        # JSON malformé
        response = self.client.patch(
            url, 
            data='{"invalid": json}', 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extreme_api_values(self):
        """Test valeurs extrêmes via API"""
        from django.urls import reverse
        
        url = reverse('revision:deck-learning-settings', args=[self.deck.id])
        
        # Valeur trop élevée
        response = self.client.patch(url, {
            'required_reviews_to_learn': 1000
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Valeur trop basse (valeur négative)
        response = self.client.patch(url, {
            'required_reviews_to_learn': -1
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_preset_with_nonexistent_deck(self):
        """Test application de preset sur deck inexistant"""
        from django.urls import reverse
        
        url = reverse('revision:deck-apply-preset', args=[99999])
        response = self.client.post(url, {
            'preset_name': 'normal'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_progress_archived_deck(self):
        """Test mise à jour progrès sur deck archivé"""
        from django.urls import reverse
        
        # Archiver le deck
        self.deck.is_archived = True
        self.deck.save()
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Archived deck card',
            back_text='Archived deck answer'
        )
        
        url = reverse('revision:flashcard-update-review-progress', args=[card.id])
        response = self.client.post(url, {
            'is_correct': True
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('archived', response.data['detail'].lower())

    def test_rate_limiting_simulation(self):
        """Test simulation de rate limiting (si implémenté)"""
        from django.urls import reverse
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Rate limit card',
            back_text='Rate limit answer'
        )
        
        url = reverse('revision:flashcard-update-review-progress', args=[card.id])
        
        # Envoyer beaucoup de requêtes rapidement
        responses = []
        for _ in range(10):
            response = self.client.post(url, {
                'is_correct': True
            }, format='json')
            responses.append(response.status_code)
        
        # Toutes devraient réussir (pas de rate limiting implémenté actuellement)
        # Mais le test est prêt si on l'ajoute plus tard
        success_count = sum(1 for status_code in responses if status_code == 200)
        self.assertGreater(success_count, 0)

    def test_invalid_preset_names(self):
        """Test noms de presets invalides"""
        from django.urls import reverse
        
        url = reverse('revision:deck-apply-preset', args=[self.deck.id])
        
        invalid_presets = [
            '',
            'invalid_preset',
            'NORMAL',  # Mauvaise casse
            'beginner_advanced',
            'null',
            None
        ]
        
        for invalid_preset in invalid_presets:
            if invalid_preset is None:
                data = {}
            else:
                data = {'preset_name': invalid_preset}
                
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_concurrent_api_requests(self):
        """Test requêtes API séquentielles (simulation de concurrence)"""
        from django.urls import reverse
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text='Sequential API card',
            back_text='Sequential API answer'
        )
        
        url = reverse('revision:flashcard-update-review-progress', args=[card.id])
        
        # Simuler des requêtes "concurrentes" de manière séquentielle
        # (Django test client n'est pas thread-safe)
        results = []
        
        for i in range(5):
            try:
                response = self.client.post(url, {
                    'is_correct': True
                }, format='json')
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        # Vérifier les résultats
        self.assertEqual(len(results), 5)
        
        # Toutes les requêtes devraient réussir en séquentiel
        success_count = sum(1 for result in results if result == 200)
        self.assertEqual(success_count, 5)
        
        # Vérifier que la carte a bien été mise à jour 5 fois
        card.refresh_from_db()
        self.assertEqual(card.total_reviews_count, 5)
        self.assertEqual(card.correct_reviews_count, 5)


class LearningSettingsValidationTest(TestCase):
    """Tests de validation des serializers"""

    def test_deck_learning_settings_serializer_validation(self):
        """Test validation complète du serializer"""
        # Données valides
        valid_data = {
            'required_reviews_to_learn': 5,
            'auto_mark_learned': True,
            'reset_on_wrong_answer': False
        }
        
        serializer = DeckLearningSettingsSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Test limites
        edge_cases = [
            ({'required_reviews_to_learn': 1}, True),    # Minimum
            ({'required_reviews_to_learn': 20}, True),   # Maximum
            ({'required_reviews_to_learn': 0}, False),   # Trop bas
            ({'required_reviews_to_learn': 21}, False),  # Trop haut
            ({'required_reviews_to_learn': -1}, False),  # Négatif
            ({'required_reviews_to_learn': 'invalid'}, False),  # Non numérique
        ]
        
        for data, should_be_valid in edge_cases:
            serializer = DeckLearningSettingsSerializer(data=data)
            if should_be_valid:
                self.assertTrue(serializer.is_valid(), f"Data {data} should be valid")
            else:
                self.assertFalse(serializer.is_valid(), f"Data {data} should be invalid")

    def test_apply_preset_serializer_validation(self):
        """Test validation du serializer de presets"""
        # Presets valides
        valid_presets = ['beginner', 'normal', 'intensive', 'expert']
        
        for preset in valid_presets:
            serializer = ApplyPresetSerializer(data={'preset_name': preset})
            self.assertTrue(serializer.is_valid(), f"Preset {preset} should be valid")
        
        # Presets invalides
        invalid_presets = ['', 'invalid', 'NORMAL', None, 123]
        
        for preset in invalid_presets:
            if preset is None:
                data = {}
            else:
                data = {'preset_name': preset}
            
            serializer = ApplyPresetSerializer(data=data)
            self.assertFalse(serializer.is_valid(), f"Preset {preset} should be invalid")