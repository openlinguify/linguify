# Tests d'intégration end-to-end pour l'app révision

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import transaction
from rest_framework.test import APITestCase
from rest_framework import status
from apps.revision.models import FlashcardDeck, Flashcard, VocabularyWord, RevisionSession
from apps.revision.serializers import FlashcardDeckSerializer, FlashcardSerializer
import json

User = get_user_model()

class DeckWorkflowIntegrationTest(APITestCase):
    """Tests d'intégration pour le workflow complet des decks"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_deck_creation_workflow(self):
        """Test du workflow complet de création d'un deck"""
        # 1. Créer un deck
        deck_data = {
            'name': 'Test Deck',
            'description': 'Test Description',
            'tags': ['python', 'django'],
            'is_public': False
        }
        
        deck_url = reverse('revision:deck-list')
        deck_response = self.client.post(deck_url, deck_data, format='json')
        
        self.assertEqual(deck_response.status_code, status.HTTP_201_CREATED)
        deck_id = deck_response.data['id']
        
        # 2. Ajouter des cartes au deck
        cards_data = [
            {
                'deck': deck_id,
                'front_text': 'Hello',
                'back_text': 'Bonjour',
                'front_language': 'en',
                'back_language': 'fr'
            },
            {
                'deck': deck_id,
                'front_text': 'Goodbye',
                'back_text': 'Au revoir',
                'front_language': 'en',
                'back_language': 'fr'
            }
        ]
        
        card_url = reverse('revision:flashcard-list')
        for card_data in cards_data:
            card_response = self.client.post(card_url, card_data, format='json')
            self.assertEqual(card_response.status_code, status.HTTP_201_CREATED)
        
        # 3. Vérifier que le deck contient les cartes
        deck_detail_url = reverse('revision:deck-detail', kwargs={'pk': deck_id})
        deck_detail_response = self.client.get(deck_detail_url)
        
        self.assertEqual(deck_detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(deck_detail_response.data['cards_count'], 2)
        self.assertEqual(deck_detail_response.data['learned_count'], 0)
        
        # 4. Récupérer les cartes du deck
        deck_cards_url = reverse('revision:deck-cards', kwargs={'pk': deck_id})
        cards_response = self.client.get(deck_cards_url)
        
        self.assertEqual(cards_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cards_response.data), 2)
        
        # 5. Marquer une carte comme apprise
        first_card_id = cards_response.data[0]['id']
        toggle_url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': first_card_id})
        toggle_response = self.client.patch(toggle_url, {'success': True}, format='json')
        
        self.assertEqual(toggle_response.status_code, status.HTTP_200_OK)
        
        # 6. Vérifier les statistiques mises à jour
        deck_detail_response = self.client.get(deck_detail_url)
        self.assertEqual(deck_detail_response.data['learned_count'], 1)
        
        # 7. Rendre le deck public
        toggle_public_url = reverse('revision:deck-toggle-public', kwargs={'pk': deck_id})
        public_response = self.client.post(toggle_public_url, {'make_public': True}, format='json')
        
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertTrue(public_response.data['is_public'])
        
        # 8. Vérifier que le deck apparaît dans les decks publics
        public_decks_url = reverse('revision:public-deck-list')
        public_decks_response = self.client.get(public_decks_url)
        
        self.assertEqual(public_decks_response.status_code, status.HTTP_200_OK)
        deck_names = [deck['name'] for deck in public_decks_response.data['results']]
        self.assertIn('Test Deck', deck_names)
    
    def test_deck_cloning_workflow(self):
        """Test du workflow de clonage d'un deck"""
        # 1. Créer un deck public avec des cartes
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Original Deck",
            description="Original Description",
            is_public=True,
            tags=['original', 'test']
        )
        
        # Ajouter des cartes
        Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text="Original Front 1",
            back_text="Original Back 1"
        )
        Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text="Original Front 2",
            back_text="Original Back 2"
        )
        
        # 2. Créer un autre utilisateur pour cloner
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        # 3. Cloner le deck
        clone_url = reverse('revision:deck-clone', kwargs={'pk': deck.id})
        clone_data = {
            'name': 'Cloned Deck',
            'description': 'Cloned Description'
        }
        clone_response = self.client.post(clone_url, clone_data, format='json')
        
        self.assertEqual(clone_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Successfully cloned', clone_response.data['message'])
        
        # 4. Vérifier que le deck cloné existe
        cloned_deck = FlashcardDeck.objects.get(name='Cloned Deck')
        self.assertEqual(cloned_deck.user, other_user)
        self.assertEqual(cloned_deck.flashcards.count(), 2)
        
        # 5. Vérifier que les cartes ont été copiées
        cloned_cards = cloned_deck.flashcards.all()
        front_texts = [card.front_text for card in cloned_cards]
        self.assertIn('Original Front 1', front_texts)
        self.assertIn('Original Front 2', front_texts)
        
        # 6. Vérifier que les cartes appartiennent au bon utilisateur
        for card in cloned_cards:
            self.assertEqual(card.user, other_user)
    
    def test_deck_archiving_workflow(self):
        """Test du workflow d'archivage d'un deck"""
        # 1. Créer un deck
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            description="Test Description"
        )
        
        # 2. Archiver le deck
        deck.archive()
        
        # 3. Vérifier que le deck est archivé
        self.assertTrue(deck.is_archived)
        self.assertIsNotNone(deck.expiration_date)
        
        # 4. Vérifier que le deck n'apparaît plus dans les listes normales
        deck_list_url = reverse('revision:deck-list')
        response = self.client.get(deck_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deck_names = [d['name'] for d in response.data['results']]
        self.assertNotIn('Test Deck', deck_names)

class LearningWorkflowIntegrationTest(APITestCase):
    """Tests d'intégration pour le workflow d'apprentissage"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Learning Deck",
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_complete_learning_workflow(self):
        """Test du workflow complet d'apprentissage"""
        # 1. Créer des cartes
        cards_data = [
            {'front_text': 'Hello', 'back_text': 'Bonjour'},
            {'front_text': 'Goodbye', 'back_text': 'Au revoir'},
            {'front_text': 'Thank you', 'back_text': 'Merci'}
        ]
        
        cards = []
        for card_data in cards_data:
            card = Flashcard.objects.create(
                user=self.user,
                deck=self.deck,
                **card_data
            )
            cards.append(card)
        
        # 2. Simuler plusieurs sessions d'apprentissage
        for card in cards:
            # Réviser chaque carte 3 fois avec succès
            for _ in range(3):
                toggle_url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': card.id})
                response = self.client.patch(toggle_url, {'success': True}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Vérifier que toutes les cartes sont marquées comme apprises
        for card in cards:
            card.refresh_from_db()
            self.assertTrue(card.learned)
        
        # 4. Vérifier les statistiques du deck
        deck_detail_url = reverse('revision:deck-detail', kwargs={'pk': self.deck.id})
        response = self.client.get(deck_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['learned_count'], 3)
        self.assertEqual(response.data['cards_count'], 3)
        
        # 5. Vérifier les statistiques utilisateur
        stats_url = reverse('revision:deck-stats')
        stats_response = self.client.get(stats_url)
        
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_response.data['totalLearned'], 3)
    
    def test_learning_preset_application(self):
        """Test d'application des presets d'apprentissage"""
        # 1. Appliquer le preset "easy"
        self.deck.apply_learning_preset('easy')
        
        self.assertEqual(self.deck.required_reviews_to_learn, 2)
        self.assertTrue(self.deck.auto_mark_learned)
        self.assertFalse(self.deck.reset_on_wrong_answer)
        
        # 2. Créer une carte et la tester
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Test",
            back_text="Test"
        )
        
        # 3. Réviser seulement 2 fois (preset easy)
        for _ in range(2):
            toggle_url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': card.id})
            response = self.client.patch(toggle_url, {'success': True}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Vérifier que la carte est apprise
        card.refresh_from_db()
        self.assertTrue(card.learned)
    
    def test_spaced_repetition_workflow(self):
        """Test du workflow de répétition espacée"""
        # 1. Créer une carte
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Spaced",
            back_text="Espacé"
        )
        
        # 2. Marquer comme révisée
        card.mark_reviewed(success=True)
        
        # 3. Vérifier qu'une prochaine révision est programmée
        self.assertIsNotNone(card.next_review)
        self.assertIsNotNone(card.last_reviewed)
        
        # 4. Vérifier les cartes dues pour révision
        due_url = reverse('revision:flashcard-due-for-review')
        response = self.client.get(due_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

class TagsWorkflowIntegrationTest(APITestCase):
    """Tests d'intégration pour le workflow des tags"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_tags_workflow(self):
        """Test du workflow complet des tags"""
        # 1. Créer des decks avec des tags
        decks_data = [
            {'name': 'Deck 1', 'tags': ['python', 'django', 'web']},
            {'name': 'Deck 2', 'tags': ['javascript', 'react', 'web']},
            {'name': 'Deck 3', 'tags': ['java', 'spring']}
        ]
        
        for deck_data in decks_data:
            deck_url = reverse('revision:deck-list')
            response = self.client.post(deck_url, deck_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Récupérer tous les tags
        tags_url = reverse('revision:tags-api')
        tags_response = self.client.get(tags_url)
        
        self.assertEqual(tags_response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', tags_response.data)
        self.assertIn('count', tags_response.data)
        
        # 3. Vérifier que tous les tags uniques sont présents
        expected_tags = {'django', 'java', 'javascript', 'python', 'react', 'spring', 'web'}
        actual_tags = set(tags_response.data['tags'])
        self.assertEqual(actual_tags, expected_tags)
        self.assertEqual(tags_response.data['count'], 7)
        
        # 4. Valider un nouveau tag
        new_tag_data = {'tag': 'new-tag'}
        validate_response = self.client.post(tags_url, new_tag_data, format='json')
        
        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(validate_response.data['tag'], 'new-tag')
        
        # 5. Essayer un tag invalide
        invalid_tag_data = {'tag': 'invalid@tag!'}
        invalid_response = self.client.post(tags_url, invalid_tag_data, format='json')
        
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('caractères non autorisés', invalid_response.data['detail'])
    
    def test_tags_filtering_workflow(self):
        """Test du workflow de filtrage par tags"""
        # 1. Créer des decks avec des tags spécifiques
        FlashcardDeck.objects.create(
            user=self.user,
            name="Python Deck",
            tags=['python', 'programming']
        )
        
        FlashcardDeck.objects.create(
            user=self.user,
            name="Java Deck",
            tags=['java', 'programming']
        )
        
        FlashcardDeck.objects.create(
            user=self.user,
            name="French Deck",
            tags=['french', 'language']
        )
        
        # 2. Récupérer tous les decks
        deck_list_url = reverse('revision:deck-list')
        all_response = self.client.get(deck_list_url)
        
        self.assertEqual(all_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(all_response.data['results']), 3)
        
        # 3. Vérifier que les tags sont présents dans les données
        for deck in all_response.data['results']:
            self.assertIn('tags', deck)
            self.assertIsInstance(deck['tags'], list)

class TransactionIntegrationTest(TransactionTestCase):
    """Tests d'intégration pour les transactions"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_deck_deletion_cascade(self):
        """Test de la suppression en cascade d'un deck"""
        # 1. Créer un deck avec des cartes
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        cards = []
        for i in range(5):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f"Front {i}",
                back_text=f"Back {i}"
            )
            cards.append(card)
        
        # 2. Créer des sessions de révision
        session = RevisionSession.objects.create(
            user=self.user,
            deck=deck,
            mode="flashcards",
            cards_studied=5,
            correct_answers=3
        )
        
        # 3. Vérifier que tout existe
        self.assertTrue(FlashcardDeck.objects.filter(id=deck.id).exists())
        self.assertEqual(Flashcard.objects.filter(deck=deck).count(), 5)
        self.assertTrue(RevisionSession.objects.filter(id=session.id).exists())
        
        # 4. Supprimer le deck
        deck.delete()
        
        # 5. Vérifier que tout a été supprimé
        self.assertFalse(FlashcardDeck.objects.filter(id=deck.id).exists())
        self.assertEqual(Flashcard.objects.filter(deck_id=deck.id).count(), 0)
        self.assertFalse(RevisionSession.objects.filter(id=session.id).exists())
    
    def test_batch_operations_transaction(self):
        """Test des opérations en lot avec transactions"""
        # 1. Créer plusieurs decks
        decks = []
        for i in range(3):
            deck = FlashcardDeck.objects.create(
                user=self.user,
                name=f"Deck {i}"
            )
            decks.append(deck)
        
        # 2. Supprimer en lot avec transaction
        with transaction.atomic():
            for deck in decks:
                deck.delete()
        
        # 3. Vérifier que tous les decks ont été supprimés
        self.assertEqual(FlashcardDeck.objects.filter(user=self.user).count(), 0)

class PerformanceIntegrationTest(APITestCase):
    """Tests d'intégration pour les performances"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_large_dataset_performance(self):
        """Test des performances avec un grand jeu de données"""
        # 1. Créer un deck avec beaucoup de cartes
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Large Deck"
        )
        
        # 2. Créer 100 cartes
        cards = []
        for i in range(100):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f"Front {i}",
                back_text=f"Back {i}"
            )
            cards.append(card)
        
        # 3. Tester les performances de listage
        deck_list_url = reverse('revision:deck-list')
        response = self.client.get(deck_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['cards_count'], 100)
        
        # 4. Tester les performances de récupération des cartes
        deck_cards_url = reverse('revision:deck-cards', kwargs={'pk': deck.id})
        cards_response = self.client.get(deck_cards_url)
        
        self.assertEqual(cards_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cards_response.data), 100)
    
    def test_concurrent_operations(self):
        """Test des opérations concurrentes"""
        # 1. Créer un deck
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Concurrent Deck"
        )
        
        # 2. Créer des cartes simultanément
        card_data = {
            'deck': deck.id,
            'front_text': 'Concurrent Front',
            'back_text': 'Concurrent Back'
        }
        
        card_url = reverse('revision:flashcard-list')
        
        # Simuler plusieurs requêtes simultanées
        responses = []
        for i in range(5):
            response = self.client.post(card_url, card_data, format='json')
            responses.append(response)
        
        # 3. Vérifier que toutes les requêtes ont réussi
        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. Vérifier que toutes les cartes ont été créées
        self.assertEqual(Flashcard.objects.filter(deck=deck).count(), 5)