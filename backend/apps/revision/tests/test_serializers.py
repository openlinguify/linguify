# Tests complets pour les sérialiseurs de l'app révision

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from apps.revision.models import FlashcardDeck, Flashcard, VocabularyWord
from apps.revision.serializers import (
    FlashcardDeckSerializer,
    FlashcardDeckDetailSerializer,
    FlashcardDeckCreateSerializer,
    FlashcardSerializer,
    VocabularyWordSerializer,
    DeckArchiveSerializer,
    DeckLearningSettingsSerializer,
    BatchDeleteSerializer,
    BatchArchiveSerializer,
    ApplyPresetSerializer
)

User = get_user_model()

class FlashcardDeckSerializerTest(TestCase):
    """Tests pour FlashcardDeckSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            description="Test Description",
            tags=['python', 'django'],
            is_public=True
        )
        
        # Créer des cartes pour les statistiques
        Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front 1",
            back_text="Back 1",
            learned=True
        )
        Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front 2",
            back_text="Back 2",
            learned=False
        )
        
        # Créer un contexte de requête
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_deck_serialization(self):
        """Test de sérialisation d'un deck"""
        serializer = FlashcardDeckSerializer(self.deck, context=self.context)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Deck')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['tags'], ['python', 'django'])
        self.assertTrue(data['is_public'])
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['cards_count'], 2)
        self.assertEqual(data['learned_count'], 1)
    
    def test_deck_deserialization(self):
        """Test de désérialisation d'un deck"""
        data = {
            'name': 'New Deck',
            'description': 'New Description',
            'tags': ['new', 'test'],
            'is_public': False
        }
        
        serializer = FlashcardDeckSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save(user=self.user)
        self.assertEqual(deck.name, 'New Deck')
        self.assertEqual(deck.tags, ['new', 'test'])
        self.assertFalse(deck.is_public)
    
    def test_deck_update(self):
        """Test de mise à jour d'un deck"""
        data = {
            'name': 'Updated Deck',
            'tags': ['updated', 'test']
        }
        
        serializer = FlashcardDeckSerializer(
            self.deck, 
            data=data, 
            partial=True,
            context=self.context
        )
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save()
        self.assertEqual(deck.name, 'Updated Deck')
        self.assertEqual(deck.tags, ['updated', 'test'])

class FlashcardDeckCreateSerializerTest(TestCase):
    """Tests pour FlashcardDeckCreateSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_create_deck_with_tags(self):
        """Test de création d'un deck avec tags"""
        data = {
            'name': 'New Deck',
            'description': 'New Description',
            'tags': ['python', 'django', 'web'],
            'is_public': True
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save(user=self.user)
        self.assertEqual(deck.name, 'New Deck')
        self.assertEqual(deck.tags, ['python', 'django', 'web'])
        self.assertTrue(deck.is_public)
    
    def test_invalid_tags_validation(self):
        """Test de validation des tags invalides"""
        data = {
            'name': 'Test Deck',
            'tags': ['valid', 'invalid@tag!', 'another']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_too_many_tags_validation(self):
        """Test de validation du nombre maximum de tags"""
        data = {
            'name': 'Test Deck',
            'tags': [f'tag{i}' for i in range(11)]  # 11 tags (max 10)
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_empty_tag_validation(self):
        """Test de validation des tags vides"""
        data = {
            'name': 'Test Deck',
            'tags': ['valid', '', 'another']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_duplicate_tags_cleaning(self):
        """Test du nettoyage des tags dupliqués"""
        data = {
            'name': 'Test Deck',
            'tags': ['python', 'PYTHON', 'django', 'Python']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save(user=self.user)
        # Les tags doivent être nettoyés et dédupliqués
        self.assertEqual(len(deck.tags), 2)
        self.assertIn('python', deck.tags)
        self.assertIn('django', deck.tags)

class FlashcardSerializerTest(TestCase):
    """Tests pour FlashcardSerializer"""
    
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
        
        self.card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front Text",
            back_text="Back Text",
            front_language="en",
            back_language="fr"
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_flashcard_serialization(self):
        """Test de sérialisation d'une flashcard"""
        serializer = FlashcardSerializer(self.card, context=self.context)
        data = serializer.data
        
        self.assertEqual(data['front_text'], 'Front Text')
        self.assertEqual(data['back_text'], 'Back Text')
        self.assertEqual(data['front_language'], 'en')
        self.assertEqual(data['back_language'], 'fr')
        self.assertEqual(data['deck'], self.deck.id)
        self.assertFalse(data['learned'])
    
    def test_flashcard_deserialization(self):
        """Test de désérialisation d'une flashcard"""
        data = {
            'front_text': 'New Front',
            'back_text': 'New Back',
            'front_language': 'es',
            'back_language': 'en',
            'deck': self.deck.id
        }
        
        serializer = FlashcardSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        card = serializer.save(user=self.user)
        self.assertEqual(card.front_text, 'New Front')
        self.assertEqual(card.back_text, 'New Back')
        self.assertEqual(card.front_language, 'es')
        self.assertEqual(card.back_language, 'en')
    
    def test_flashcard_validation(self):
        """Test de validation d'une flashcard"""
        # Test avec texte vide
        data = {
            'front_text': '',
            'back_text': 'Back Text',
            'deck': self.deck.id
        }
        
        serializer = FlashcardSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('front_text', serializer.errors)
    
    def test_flashcard_update(self):
        """Test de mise à jour d'une flashcard"""
        data = {
            'front_text': 'Updated Front',
            'learned': True
        }
        
        serializer = FlashcardSerializer(
            self.card,
            data=data,
            partial=True,
            context=self.context
        )
        self.assertTrue(serializer.is_valid())
        
        card = serializer.save()
        self.assertEqual(card.front_text, 'Updated Front')
        self.assertTrue(card.learned)

class DeckLearningSettingsSerializerTest(TestCase):
    """Tests pour DeckLearningSettingsSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_learning_settings_serialization(self):
        """Test de sérialisation des paramètres d'apprentissage"""
        serializer = DeckLearningSettingsSerializer(self.deck, context=self.context)
        data = serializer.data
        
        self.assertEqual(data['required_reviews_to_learn'], 3)
        self.assertTrue(data['auto_mark_learned'])
        self.assertFalse(data['reset_on_wrong_answer'])
    
    def test_learning_settings_update(self):
        """Test de mise à jour des paramètres d'apprentissage"""
        data = {
            'required_reviews_to_learn': 5,
            'auto_mark_learned': False,
            'reset_on_wrong_answer': True
        }
        
        serializer = DeckLearningSettingsSerializer(
            self.deck,
            data=data,
            partial=True,
            context=self.context
        )
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save()
        self.assertEqual(deck.required_reviews_to_learn, 5)
        self.assertFalse(deck.auto_mark_learned)
        self.assertTrue(deck.reset_on_wrong_answer)
    
    def test_invalid_reviews_validation(self):
        """Test de validation du nombre de révisions invalide"""
        data = {
            'required_reviews_to_learn': 0  # Doit être >= 1
        }
        
        serializer = DeckLearningSettingsSerializer(
            self.deck,
            data=data,
            partial=True,
            context=self.context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('required_reviews_to_learn', serializer.errors)

class BatchDeleteSerializerTest(TestCase):
    """Tests pour BatchDeleteSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck1 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 1"
        )
        self.deck2 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 2"
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_valid_batch_delete(self):
        """Test de suppression en lot valide"""
        data = {
            'deck_ids': [self.deck1.id, self.deck2.id]
        }
        
        serializer = BatchDeleteSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        result = serializer.save()
        self.assertIn('deleted', result)
        self.assertEqual(result['deleted'], 2)
    
    def test_empty_deck_ids_validation(self):
        """Test de validation des IDs vides"""
        data = {
            'deck_ids': []
        }
        
        serializer = BatchDeleteSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('deck_ids', serializer.errors)
    
    def test_invalid_deck_ids_validation(self):
        """Test de validation des IDs invalides"""
        data = {
            'deck_ids': [999, 1000]  # IDs qui n'existent pas
        }
        
        serializer = BatchDeleteSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('deck_ids', serializer.errors)

class BatchArchiveSerializerTest(TestCase):
    """Tests pour BatchArchiveSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.deck1 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 1"
        )
        self.deck2 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 2"
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_valid_batch_archive(self):
        """Test d'archivage en lot valide"""
        data = {
            'deck_ids': [self.deck1.id, self.deck2.id],
            'action': 'archive'
        }
        
        serializer = BatchArchiveSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        result = serializer.save()
        self.assertIn('updated', result)
        self.assertEqual(result['updated'], 2)
        self.assertEqual(result['action'], 'archive')
    
    def test_valid_batch_unarchive(self):
        """Test de désarchivage en lot valide"""
        # Archiver d'abord les decks
        self.deck1.archive()
        self.deck2.archive()
        
        data = {
            'deck_ids': [self.deck1.id, self.deck2.id],
            'action': 'unarchive'
        }
        
        serializer = BatchArchiveSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        result = serializer.save()
        self.assertIn('updated', result)
        self.assertEqual(result['updated'], 2)
        self.assertEqual(result['action'], 'unarchive')
    
    def test_invalid_action_validation(self):
        """Test de validation d'action invalide"""
        data = {
            'deck_ids': [self.deck1.id],
            'action': 'invalid_action'
        }
        
        serializer = BatchArchiveSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('action', serializer.errors)

class ApplyPresetSerializerTest(TestCase):
    """Tests pour ApplyPresetSerializer"""
    
    def test_valid_preset_name(self):
        """Test de nom de preset valide"""
        data = {'preset_name': 'beginner'}
        
        serializer = ApplyPresetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['preset_name'], 'beginner')
    
    def test_invalid_preset_name(self):
        """Test de nom de preset invalide"""
        data = {'preset_name': 'invalid_preset'}
        
        serializer = ApplyPresetSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preset_name', serializer.errors)
    
    def test_empty_preset_name(self):
        """Test de nom de preset vide"""
        data = {'preset_name': ''}
        
        serializer = ApplyPresetSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('preset_name', serializer.errors)

class VocabularyWordSerializerTest(TestCase):
    """Tests pour VocabularyWordSerializer"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.word = VocabularyWord.objects.create(
            user=self.user,
            word="hello",
            translation="bonjour",
            language="en",
            definition="A greeting"
        )
        
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        self.context = {'request': Request(request)}
    
    def test_vocabulary_serialization(self):
        """Test de sérialisation d'un mot de vocabulaire"""
        serializer = VocabularyWordSerializer(self.word, context=self.context)
        data = serializer.data
        
        self.assertEqual(data['word'], 'hello')
        self.assertEqual(data['translation'], 'bonjour')
        self.assertEqual(data['language'], 'en')
        self.assertEqual(data['definition'], 'A greeting')
    
    def test_vocabulary_deserialization(self):
        """Test de désérialisation d'un mot de vocabulaire"""
        data = {
            'word': 'goodbye',
            'translation': 'au revoir',
            'language': 'en',
            'definition': 'A farewell'
        }
        
        serializer = VocabularyWordSerializer(data=data, context=self.context)
        self.assertTrue(serializer.is_valid())
        
        word = serializer.save(user=self.user)
        self.assertEqual(word.word, 'goodbye')
        self.assertEqual(word.translation, 'au revoir')
        self.assertEqual(word.language, 'en')
        self.assertEqual(word.definition, 'A farewell')
    
    def test_vocabulary_validation(self):
        """Test de validation d'un mot de vocabulaire"""
        # Test avec mot vide
        data = {
            'word': '',
            'translation': 'bonjour',
            'language': 'en'
        }
        
        serializer = VocabularyWordSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn('word', serializer.errors)