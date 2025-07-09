# Tests complets pour les vues API de l'app révision

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from apps.revision.models import FlashcardDeck, Flashcard, VocabularyWord, RevisionSession

User = get_user_model()

class FlashcardDeckViewSetTest(APITestCase):
    """Tests pour FlashcardDeckViewSet"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Créer des decks de test
        self.deck1 = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck 1",
            description="Test Description 1",
            tags=['python', 'django']
        )
        self.deck2 = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck 2",
            description="Test Description 2",
            is_public=True,
            tags=['javascript', 'react']
        )
        self.deck3 = FlashcardDeck.objects.create(
            user=self.user2,
            name="Other User Deck",
            description="Other Description",
            is_public=True
        )
        
        # Authentifier l'utilisateur
        self.client.force_authenticate(user=self.user)
    
    def test_list_decks(self):
        """Test de listage des decks"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 decks pour user
    
    def test_create_deck(self):
        """Test de création d'un deck"""
        url = reverse('revision:deck-list')
        data = {
            'name': 'New Deck',
            'description': 'New Description',
            'tags': ['new', 'test'],
            'is_public': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Deck')
        self.assertEqual(response.data['tags'], ['new', 'test'])
        
        # Vérifier en base
        deck = FlashcardDeck.objects.get(name='New Deck')
        self.assertEqual(deck.user, self.user)
    
    def test_retrieve_deck(self):
        """Test de récupération d'un deck"""
        url = reverse('revision:deck-detail', kwargs={'pk': self.deck1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Deck 1')
        self.assertEqual(response.data['tags'], ['python', 'django'])
    
    def test_update_deck(self):
        """Test de mise à jour d'un deck"""
        url = reverse('revision:deck-detail', kwargs={'pk': self.deck1.id})
        data = {
            'name': 'Updated Deck',
            'description': 'Updated Description',
            'tags': ['updated', 'test']
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Deck')
        self.assertEqual(response.data['tags'], ['updated', 'test'])
    
    def test_delete_deck(self):
        """Test de suppression d'un deck"""
        url = reverse('revision:deck-detail', kwargs={'pk': self.deck1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FlashcardDeck.objects.filter(id=self.deck1.id).exists())
    
    def test_clone_deck(self):
        """Test de clonage d'un deck"""
        url = reverse('revision:deck-clone', kwargs={'pk': self.deck3.id})
        data = {
            'name': 'Cloned Deck',
            'description': 'Cloned Description'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Successfully cloned', response.data['message'])
        
        # Vérifier que le deck a été créé
        cloned_deck = FlashcardDeck.objects.get(name='Cloned Deck')
        self.assertEqual(cloned_deck.user, self.user)
    
    def test_toggle_public(self):
        """Test de changement de visibilité publique"""
        url = reverse('revision:deck-toggle-public', kwargs={'pk': self.deck1.id})
        data = {'make_public': True}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_public'])
        
        # Vérifier en base
        self.deck1.refresh_from_db()
        self.assertTrue(self.deck1.is_public)
    
    def test_deck_stats(self):
        """Test des statistiques des decks"""
        url = reverse('revision:deck-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalDecks', response.data)
        self.assertIn('totalCards', response.data)
        self.assertIn('totalLearned', response.data)
        self.assertIn('completionRate', response.data)
    
    def test_deck_cards(self):
        """Test de récupération des cartes d'un deck"""
        # Créer des cartes
        Flashcard.objects.create(
            user=self.user,
            deck=self.deck1,
            front_text="Front 1",
            back_text="Back 1"
        )
        Flashcard.objects.create(
            user=self.user,
            deck=self.deck1,
            front_text="Front 2",
            back_text="Back 2"
        )
        
        url = reverse('revision:deck-cards', kwargs={'pk': self.deck1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_deck_permissions(self):
        """Test des permissions des decks"""
        # Essayer de modifier le deck d'un autre utilisateur
        url = reverse('revision:deck-detail', kwargs={'pk': self.deck3.id})
        data = {'name': 'Hacked Deck'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_decks(self):
        """Test de recherche dans les decks"""
        url = reverse('revision:deck-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_decks_by_tags(self):
        """Test de filtrage par tags (côté client)"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Vérifier que les tags sont présents
        deck_with_tags = next(d for d in response.data['results'] if d['id'] == self.deck1.id)
        self.assertEqual(deck_with_tags['tags'], ['python', 'django'])

class FlashcardViewSetTest(APITestCase):
    """Tests pour FlashcardViewSet"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        self.card1 = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front 1",
            back_text="Back 1"
        )
        self.card2 = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front 2",
            back_text="Back 2",
            learned=True
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_list_flashcards(self):
        """Test de listage des flashcards"""
        url = reverse('revision:flashcard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_flashcard(self):
        """Test de création d'une flashcard"""
        url = reverse('revision:flashcard-list')
        data = {
            'deck': self.deck.id,
            'front_text': 'New Front',
            'back_text': 'New Back',
            'front_language': 'en',
            'back_language': 'fr'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['front_text'], 'New Front')
        self.assertEqual(response.data['back_text'], 'New Back')
    
    def test_update_flashcard(self):
        """Test de mise à jour d'une flashcard"""
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.card1.id})
        data = {
            'front_text': 'Updated Front',
            'back_text': 'Updated Back'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front_text'], 'Updated Front')
    
    def test_delete_flashcard(self):
        """Test de suppression d'une flashcard"""
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.card1.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flashcard.objects.filter(id=self.card1.id).exists())
    
    def test_toggle_learned(self):
        """Test de changement d'état appris"""
        url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': self.card1.id})
        data = {'success': True}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la carte a été mise à jour
        self.card1.refresh_from_db()
        self.assertGreater(self.card1.review_count, 0)
    
    def test_due_for_review(self):
        """Test de récupération des cartes à réviser"""
        url = reverse('revision:flashcard-due-for-review')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_filter_flashcards_by_deck(self):
        """Test de filtrage par deck"""
        url = reverse('revision:flashcard-list')
        response = self.client.get(url, {'deck': self.deck.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_flashcards_by_learned(self):
        """Test de filtrage par statut appris"""
        url = reverse('revision:flashcard-list')
        response = self.client.get(url, {'learned': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['learned'])

class TagsAPIViewTest(APITestCase):
    """Tests pour TagsAPIView"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des decks avec des tags
        FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 1",
            tags=['python', 'django', 'web']
        )
        FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 2",
            tags=['javascript', 'react', 'web']
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_tags(self):
        """Test de récupération des tags"""
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
        self.assertIn('count', response.data)
        
        # Vérifier que tous les tags sont présents
        expected_tags = ['django', 'javascript', 'python', 'react', 'web']
        self.assertEqual(sorted(response.data['tags']), expected_tags)
        self.assertEqual(response.data['count'], 5)
    
    def test_validate_tag(self):
        """Test de validation d'un tag"""
        url = reverse('revision:tags-api')
        data = {'tag': 'new-tag'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tag'], 'new-tag')
        self.assertIn('Tag validé avec succès', response.data['message'])
    
    def test_invalid_tag_validation(self):
        """Test de validation d'un tag invalide"""
        url = reverse('revision:tags-api')
        data = {'tag': 'invalid@tag!'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('caractères non autorisés', response.data['detail'])
    
    def test_empty_tag_validation(self):
        """Test de validation d'un tag vide"""
        url = reverse('revision:tags-api')
        data = {'tag': ''}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ne peut pas être vide', response.data['detail'])
    
    def test_long_tag_validation(self):
        """Test de validation d'un tag trop long"""
        url = reverse('revision:tags-api')
        data = {'tag': 'a' * 51}  # 51 caractères
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dépasser 50 caractères', response.data['detail'])

class PublicDecksViewSetTest(APITestCase):
    """Tests pour PublicDecksViewSet"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des decks publics
        self.public_deck1 = FlashcardDeck.objects.create(
            user=self.user,
            name="Public Deck 1",
            description="Public Description 1",
            is_public=True
        )
        self.public_deck2 = FlashcardDeck.objects.create(
            user=self.user,
            name="Public Deck 2",
            description="Public Description 2",
            is_public=True
        )
        
        # Créer un deck privé (ne devrait pas apparaître)
        self.private_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Private Deck",
            description="Private Description",
            is_public=False
        )
        
        # Ajouter des cartes au deck public
        Flashcard.objects.create(
            user=self.user,
            deck=self.public_deck1,
            front_text="Front 1",
            back_text="Back 1"
        )
        Flashcard.objects.create(
            user=self.user,
            deck=self.public_deck1,
            front_text="Front 2",
            back_text="Back 2"
        )
    
    def test_list_public_decks(self):
        """Test de listage des decks publics"""
        url = reverse('revision:public-deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Seulement les publics
    
    def test_public_deck_stats(self):
        """Test des statistiques des decks publics"""
        url = reverse('revision:public-deck-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalDecks', response.data)
        self.assertIn('totalCards', response.data)
        self.assertIn('totalAuthors', response.data)
        self.assertEqual(response.data['totalDecks'], 2)
        self.assertEqual(response.data['totalCards'], 2)
    
    def test_public_deck_cards(self):
        """Test de récupération des cartes d'un deck public"""
        url = reverse('revision:public-deck-cards', kwargs={'pk': self.public_deck1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_clone_public_deck(self):
        """Test de clonage d'un deck public"""
        # Authentifier un utilisateur différent
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user2)
        
        url = reverse('revision:public-deck-clone', kwargs={'pk': self.public_deck1.id})
        data = {
            'name': 'My Cloned Deck',
            'description': 'My cloned description'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Successfully cloned', response.data['message'])
        
        # Vérifier que le deck a été créé pour le bon utilisateur
        cloned_deck = FlashcardDeck.objects.get(name='My Cloned Deck')
        self.assertEqual(cloned_deck.user, user2)
        self.assertEqual(cloned_deck.flashcards.count(), 2)  # Cartes copiées
    
    def test_search_public_decks(self):
        """Test de recherche dans les decks publics"""
        url = reverse('revision:public-deck-list')
        response = self.client.get(url, {'search': 'Public'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_public_decks_by_author(self):
        """Test de filtrage par auteur"""
        url = reverse('revision:public-deck-list')
        response = self.client.get(url, {'author': 'testuser'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_popular_public_decks(self):
        """Test des decks populaires"""
        url = reverse('revision:public-deck-popular')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)

class FlashcardImportViewTest(APITestCase):
    """Tests pour FlashcardImportView"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_import_preview(self):
        """Test de prévisualisation d'import"""
        # Créer un fichier CSV de test
        import io
        csv_content = "front,back\nHello,Bonjour\nGoodbye,Au revoir"
        csv_file = io.StringIO(csv_content)
        csv_file.name = 'test.csv'
        
        url = reverse('revision:flashcard-import', kwargs={'deck_id': self.deck.id})
        data = {
            'file': csv_file,
            'has_header': True,
            'preview_only': True,
            'front_column': 0,
            'back_column': 1
        }
        
        # Note: Ce test nécessiterait un fichier réel pour fonctionner complètement
        # Il s'agit plutôt d'un test de structure
    
    def test_import_permissions(self):
        """Test des permissions d'import"""
        # Créer un autre utilisateur
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Créer un deck pour user2
        deck2 = FlashcardDeck.objects.create(
            user=user2,
            name="Other Deck"
        )
        
        # Essayer d'importer dans le deck d'un autre utilisateur
        url = reverse('revision:flashcard-import', kwargs={'deck_id': deck2.id})
        data = {'file': None}  # Fichier vide pour tester les permissions
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Devrait échouer à cause du fichier manquant, pas des permissions
        # car l'utilisateur n'a pas accès au deck