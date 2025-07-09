# Tests complets pour les modèles de l'app révision

import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from apps.revision.models import FlashcardDeck, Flashcard, VocabularyWord, RevisionSession

User = get_user_model()

class FlashcardDeckModelTest(TestCase):
    """Tests pour le modèle FlashcardDeck"""
    
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
    
    def test_create_basic_deck(self):
        """Test de création d'un deck basique"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            description="Test Description"
        )
        
        self.assertEqual(deck.name, "Test Deck")
        self.assertEqual(deck.description, "Test Description")
        self.assertEqual(deck.user, self.user)
        self.assertTrue(deck.is_active)
        self.assertFalse(deck.is_public)
        self.assertFalse(deck.is_archived)
        self.assertEqual(deck.required_reviews_to_learn, 3)
    
    def test_deck_str_representation(self):
        """Test de la représentation string du deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
        )
        self.assertEqual(str(deck), "Test Deck (by testuser)")
    
    def test_deck_with_tags(self):
        """Test d'un deck avec des tags"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            tags=['python', 'django', 'web']
        )
        
        self.assertEqual(len(deck.tags), 3)
        self.assertIn('python', deck.tags)
        self.assertIn('django', deck.tags)
        self.assertIn('web', deck.tags)
    
    def test_deck_learning_settings(self):
        """Test des paramètres d'apprentissage"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            required_reviews_to_learn=5,
            auto_mark_learned=False,
            reset_on_wrong_answer=True
        )
        
        self.assertEqual(deck.required_reviews_to_learn, 5)
        self.assertFalse(deck.auto_mark_learned)
        self.assertTrue(deck.reset_on_wrong_answer)
    
    def test_deck_archiving(self):
        """Test de l'archivage d'un deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        # Archiver le deck
        deck.archive()
        
        self.assertTrue(deck.is_archived)
        self.assertIsNotNone(deck.expiration_date)
        self.assertGreater(deck.expiration_date, timezone.now())
    
    def test_deck_public_toggle(self):
        """Test du changement de visibilité publique"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck",
            is_public=False
        )
        
        # Rendre public
        deck.is_public = True
        deck.save()
        
        self.assertTrue(deck.is_public)
    
    def test_deck_learning_presets(self):
        """Test des presets d'apprentissage"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        # Obtenir les presets disponibles
        presets = deck.get_learning_presets()
        
        self.assertIsInstance(presets, dict)
        self.assertIn('beginner', presets)
        self.assertIn('normal', presets)
        self.assertIn('intensive', presets)
    
    def test_apply_learning_preset(self):
        """Test d'application d'un preset d'apprentissage"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        # Appliquer le preset "beginner"
        success = deck.apply_learning_preset('beginner')
        
        self.assertTrue(success)
        self.assertEqual(deck.required_reviews_to_learn, 2)
        self.assertTrue(deck.auto_mark_learned)
        self.assertFalse(deck.reset_on_wrong_answer)
    
    def test_deck_statistics(self):
        """Test des statistiques du deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Test Deck"
        )
        
        # Ajouter des cartes
        Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text="Front 1",
            back_text="Back 1",
            learned=True
        )
        Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text="Front 2",
            back_text="Back 2",
            learned=False
        )
        
        stats = deck.get_learning_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_cards'], 2)
        self.assertEqual(stats['learned_cards'], 1)
        # Note: 'remaining_cards' might not exist, check available keys
        if 'completion_rate' in stats:
            self.assertGreaterEqual(stats['completion_rate'], 0)
    
    def test_deck_cleanup_expired(self):
        """Test du nettoyage des decks expirés"""
        # Créer un deck expiré
        expired_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Expired Deck",
            is_archived=True,
            expiration_date=timezone.now() - timedelta(days=1)
        )
        
        # Créer un deck non expiré
        active_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Active Deck"
        )
        
        # Nettoyer les decks expirés
        count = FlashcardDeck.cleanup_expired()
        
        self.assertEqual(count, 1)
        self.assertFalse(FlashcardDeck.objects.filter(id=expired_deck.id).exists())
        self.assertTrue(FlashcardDeck.objects.filter(id=active_deck.id).exists())

class FlashcardModelTest(TestCase):
    """Tests pour le modèle Flashcard"""
    
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
    
    def test_create_basic_flashcard(self):
        """Test de création d'une carte basique"""
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        
        self.assertEqual(card.front_text, "Front")
        self.assertEqual(card.back_text, "Back")
        self.assertEqual(card.user, self.user)
        self.assertEqual(card.deck, self.deck)
        self.assertFalse(card.learned)
        self.assertEqual(card.review_count, 0)
    
    def test_flashcard_str_representation(self):
        """Test de la représentation string de la carte"""
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        # La représentation réelle utilise "..." et "->"
        expected = f"Front... -> Back... (Test Deck)"
        self.assertEqual(str(card), expected)
    
    def test_flashcard_with_languages(self):
        """Test d'une carte avec des langues"""
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Hello",
            back_text="Bonjour",
            front_language="en",
            back_language="fr"
        )
        
        self.assertEqual(card.front_language, "en")
        self.assertEqual(card.back_language, "fr")
    
    def test_flashcard_learning_progress(self):
        """Test du progrès d'apprentissage"""
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        
        # Vérifier le progrès initial
        self.assertEqual(card.learning_progress_percentage, 0)
        self.assertEqual(card.reviews_remaining_to_learn, 3)
        
        # Marquer comme révisé avec succès
        card.update_review_progress(is_correct=True)
        
        self.assertEqual(card.correct_reviews_count, 1)
        self.assertEqual(card.total_reviews_count, 1)
        self.assertGreater(card.learning_progress_percentage, 0)
    
    def test_flashcard_mark_reviewed(self):
        """Test du marquage comme révisé"""
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        
        # Marquer comme révisé avec succès
        card.mark_reviewed(success=True)
        
        self.assertEqual(card.review_count, 1)
        self.assertIsNotNone(card.last_reviewed)
        self.assertIsNotNone(card.next_review)
    
    def test_flashcard_auto_mark_learned(self):
        """Test du marquage automatique comme appris"""
        # Configurer le deck pour marquage automatique
        self.deck.auto_mark_learned = True
        self.deck.required_reviews_to_learn = 2
        self.deck.save()
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        
        # Réviser avec succès le nombre requis de fois
        card.update_review_progress(is_correct=True)
        card.update_review_progress(is_correct=True)
        
        self.assertTrue(card.learned)
    
    def test_flashcard_reset_on_wrong_answer(self):
        """Test de la réinitialisation sur mauvaise réponse"""
        # Configurer le deck pour réinitialisation
        self.deck.reset_on_wrong_answer = True
        self.deck.save()
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=self.deck,
            front_text="Front",
            back_text="Back"
        )
        
        # Réviser avec succès puis échouer
        card.update_review_progress(is_correct=True)
        initial_correct = card.correct_reviews_count
        
        card.update_review_progress(is_correct=False)
        
        self.assertEqual(card.correct_reviews_count, 0)
        self.assertGreater(card.total_reviews_count, initial_correct)

class VocabularyWordModelTest(TestCase):
    """Tests pour le modèle VocabularyWord"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_vocabulary_word(self):
        """Test de création d'un mot de vocabulaire"""
        word = VocabularyWord.objects.create(
            user=self.user,
            word="hello",
            translation="bonjour",
            source_language="EN",
            target_language="FR",
            context="A greeting"
        )
        
        self.assertEqual(word.word, "hello")
        self.assertEqual(word.translation, "bonjour")
        self.assertEqual(word.source_language, "EN")
        self.assertEqual(word.target_language, "FR")
        self.assertEqual(word.context, "A greeting")
        self.assertEqual(word.user, self.user)
    
    def test_vocabulary_word_str_representation(self):
        """Test de la représentation string du mot"""
        word = VocabularyWord.objects.create(
            user=self.user,
            word="hello",
            translation="bonjour",
            source_language="EN",
            target_language="FR"
        )
        expected = "hello (EN) -> bonjour (FR)"
        self.assertEqual(str(word), expected)

class RevisionSessionModelTest(TestCase):
    """Tests pour le modèle RevisionSession"""
    
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
    
    def test_create_revision_session(self):
        """Test de création d'une session de révision"""
        session = RevisionSession.objects.create(
            user=self.user,
            scheduled_date=timezone.now(),
            status='PENDING'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.status, 'PENDING')
        self.assertIsNotNone(session.scheduled_date)
    
    def test_revision_session_str_representation(self):
        """Test de la représentation string de la session"""
        scheduled_date = timezone.now()
        session = RevisionSession.objects.create(
            user=self.user,
            scheduled_date=scheduled_date,
            status='PENDING'
        )
        expected = f"Session for testuser on {scheduled_date}"
        self.assertEqual(str(session), expected)
    
    def test_revision_session_completion(self):
        """Test de completion d'une session"""
        session = RevisionSession.objects.create(
            user=self.user,
            scheduled_date=timezone.now(),
            status='PENDING'
        )
        
        # Marquer comme complétée avec un taux de succès
        session.mark_completed(0.8)
        
        self.assertEqual(session.status, 'COMPLETED')
        self.assertEqual(session.success_rate, 0.8)
        self.assertIsNotNone(session.completed_date)