# Tests complets pour les permissions de l'app révision

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from apps.revision.models import FlashcardDeck, Flashcard, VocabularyWord, RevisionSession
from apps.revision.permissions import FlashcardDeckPermission, FlashcardPermission, IsOwnerOrReadOnlyPublic

User = get_user_model()

class PermissionTestCase(APITestCase):
    """Tests de base pour les permissions"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Créer des decks pour les tests
        self.private_deck = FlashcardDeck.objects.create(
            user=self.user1,
            name="Private Deck",
            description="Private Description",
            is_public=False
        )
        
        self.public_deck = FlashcardDeck.objects.create(
            user=self.user1,
            name="Public Deck",
            description="Public Description",
            is_public=True
        )
        
        # Créer des flashcards
        self.private_card = Flashcard.objects.create(
            user=self.user1,
            deck=self.private_deck,
            front_text="Private Front",
            back_text="Private Back"
        )
        
        self.public_card = Flashcard.objects.create(
            user=self.user1,
            deck=self.public_deck,
            front_text="Public Front",
            back_text="Public Back"
        )

class DeckPermissionTest(PermissionTestCase):
    """Tests des permissions pour les decks"""
    
    def test_owner_can_view_private_deck(self):
        """Test que le propriétaire peut voir son deck privé"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Private Deck')
    
    def test_owner_can_edit_private_deck(self):
        """Test que le propriétaire peut modifier son deck privé"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        data = {'name': 'Updated Private Deck'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Private Deck')
    
    def test_owner_can_delete_private_deck(self):
        """Test que le propriétaire peut supprimer son deck privé"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FlashcardDeck.objects.filter(id=self.private_deck.id).exists())
    
    def test_other_user_cannot_view_private_deck(self):
        """Test qu'un autre utilisateur ne peut pas voir un deck privé"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_other_user_cannot_edit_private_deck(self):
        """Test qu'un autre utilisateur ne peut pas modifier un deck privé"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        data = {'name': 'Hacked Deck'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_other_user_cannot_delete_private_deck(self):
        """Test qu'un autre utilisateur ne peut pas supprimer un deck privé"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_other_user_can_view_public_deck(self):
        """Test qu'un autre utilisateur peut voir un deck public"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.public_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Public Deck')
    
    def test_other_user_cannot_edit_public_deck(self):
        """Test qu'un autre utilisateur ne peut pas modifier un deck public"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.public_deck.id})
        data = {'name': 'Hacked Public Deck'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_other_user_cannot_delete_public_deck(self):
        """Test qu'un autre utilisateur ne peut pas supprimer un deck public"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-detail', kwargs={'pk': self.public_deck.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_other_user_can_clone_public_deck(self):
        """Test qu'un autre utilisateur peut cloner un deck public"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-clone', kwargs={'pk': self.public_deck.id})
        data = {
            'name': 'Cloned Public Deck',
            'description': 'Cloned Description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Successfully cloned', response.data['message'])
    
    def test_other_user_cannot_clone_private_deck(self):
        """Test qu'un autre utilisateur ne peut pas cloner un deck privé"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-clone', kwargs={'pk': self.private_deck.id})
        data = {
            'name': 'Cloned Private Deck',
            'description': 'Cloned Description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FlashcardPermissionTest(PermissionTestCase):
    """Tests des permissions pour les flashcards"""
    
    def test_owner_can_view_private_flashcard(self):
        """Test que le propriétaire peut voir sa carte privée"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.private_card.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front_text'], 'Private Front')
    
    def test_owner_can_edit_private_flashcard(self):
        """Test que le propriétaire peut modifier sa carte privée"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.private_card.id})
        data = {'front_text': 'Updated Private Front'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front_text'], 'Updated Private Front')
    
    def test_owner_can_delete_private_flashcard(self):
        """Test que le propriétaire peut supprimer sa carte privée"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.private_card.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flashcard.objects.filter(id=self.private_card.id).exists())
    
    def test_other_user_cannot_view_private_flashcard(self):
        """Test qu'un autre utilisateur ne peut pas voir une carte privée"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.private_card.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_other_user_cannot_edit_private_flashcard(self):
        """Test qu'un autre utilisateur ne peut pas modifier une carte privée"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.private_card.id})
        data = {'front_text': 'Hacked Front'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_other_user_can_view_public_flashcard(self):
        """Test qu'un autre utilisateur peut voir une carte publique"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.public_card.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front_text'], 'Public Front')
    
    def test_other_user_cannot_edit_public_flashcard(self):
        """Test qu'un autre utilisateur ne peut pas modifier une carte publique"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.public_card.id})
        data = {'front_text': 'Hacked Public Front'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_other_user_cannot_delete_public_flashcard(self):
        """Test qu'un autre utilisateur ne peut pas supprimer une carte publique"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-detail', kwargs={'pk': self.public_card.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AnonymousUserPermissionTest(PermissionTestCase):
    """Tests des permissions pour les utilisateurs anonymes"""
    
    def test_anonymous_cannot_view_private_deck(self):
        """Test qu'un utilisateur anonyme ne peut pas voir un deck privé"""
        url = reverse('revision:deck-detail', kwargs={'pk': self.private_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_cannot_view_public_deck(self):
        """Test qu'un utilisateur anonyme ne peut pas voir un deck public"""
        url = reverse('revision:deck-detail', kwargs={'pk': self.public_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_cannot_create_deck(self):
        """Test qu'un utilisateur anonyme ne peut pas créer un deck"""
        url = reverse('revision:deck-list')
        data = {
            'name': 'Anonymous Deck',
            'description': 'Anonymous Description'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_cannot_create_flashcard(self):
        """Test qu'un utilisateur anonyme ne peut pas créer une carte"""
        url = reverse('revision:flashcard-list')
        data = {
            'deck': self.public_deck.id,
            'front_text': 'Anonymous Front',
            'back_text': 'Anonymous Back'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_can_view_public_decks_list(self):
        """Test qu'un utilisateur anonyme peut voir la liste des decks publics"""
        url = reverse('revision:public-deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Public Deck')
    
    def test_anonymous_can_view_public_deck_cards(self):
        """Test qu'un utilisateur anonyme peut voir les cartes d'un deck public"""
        url = reverse('revision:public-deck-cards', kwargs={'pk': self.public_deck.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['front_text'], 'Public Front')

class ListingPermissionTest(PermissionTestCase):
    """Tests des permissions pour les listes"""
    
    def test_user_sees_only_own_decks_in_list(self):
        """Test qu'un utilisateur ne voit que ses propres decks dans la liste"""
        # Créer un deck pour user2
        user2_deck = FlashcardDeck.objects.create(
            user=self.user2,
            name="User2 Deck",
            description="User2 Description",
            is_public=True
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deck_names = [deck['name'] for deck in response.data['results']]
        
        # User1 devrait voir ses 2 decks mais pas celui de user2
        self.assertIn('Private Deck', deck_names)
        self.assertIn('Public Deck', deck_names)
        self.assertNotIn('User2 Deck', deck_names)
    
    def test_user_sees_only_own_flashcards_in_list(self):
        """Test qu'un utilisateur ne voit que ses propres cartes dans la liste"""
        # Créer un deck et une carte pour user2
        user2_deck = FlashcardDeck.objects.create(
            user=self.user2,
            name="User2 Deck",
            description="User2 Description"
        )
        
        user2_card = Flashcard.objects.create(
            user=self.user2,
            deck=user2_deck,
            front_text="User2 Front",
            back_text="User2 Back"
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:flashcard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        card_fronts = [card['front_text'] for card in response.data['results']]
        
        # User1 devrait voir ses 2 cartes mais pas celle de user2
        self.assertIn('Private Front', card_fronts)
        self.assertIn('Public Front', card_fronts)
        self.assertNotIn('User2 Front', card_fronts)

class ActionPermissionTest(PermissionTestCase):
    """Tests des permissions pour les actions spécifiques"""
    
    def test_owner_can_toggle_deck_public(self):
        """Test que le propriétaire peut changer la visibilité de son deck"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-toggle-public', kwargs={'pk': self.private_deck.id})
        data = {'make_public': True}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_public'])
    
    def test_other_user_cannot_toggle_deck_public(self):
        """Test qu'un autre utilisateur ne peut pas changer la visibilité d'un deck"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:deck-toggle-public', kwargs={'pk': self.public_deck.id})
        data = {'make_public': False}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_owner_can_toggle_flashcard_learned(self):
        """Test que le propriétaire peut marquer sa carte comme apprise"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': self.private_card.id})
        data = {'success': True}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_other_user_cannot_toggle_flashcard_learned(self):
        """Test qu'un autre utilisateur ne peut pas marquer une carte comme apprise"""
        self.client.force_authenticate(user=self.user2)
        url = reverse('revision:flashcard-toggle-learned', kwargs={'pk': self.public_card.id})
        data = {'success': True}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_access_own_stats(self):
        """Test qu'un utilisateur peut accéder à ses propres statistiques"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:deck-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('totalDecks', response.data)
    
    def test_tags_api_requires_authentication(self):
        """Test que l'API des tags requiert une authentification"""
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access_tags(self):
        """Test qu'un utilisateur authentifié peut accéder aux tags"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)