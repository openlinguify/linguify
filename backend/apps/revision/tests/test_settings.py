# -*- coding: utf-8 -*-
# backend/apps/revision/tests/test_settings.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.revision.models.settings_models import RevisionSettings, RevisionSessionConfig

User = get_user_model()


class RevisionSettingsModelTest(TestCase):
    """Tests pour les modeles de parametres de revision"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_revision_settings_creation(self):
        """Test de creation des parametres de revision"""
        settings, created = RevisionSettings.objects.get_or_create(user=self.user)
        
        self.assertEqual(settings.user, self.user)
        self.assertEqual(settings.default_study_mode, 'spaced')
        self.assertEqual(settings.default_difficulty, 'normal')
        self.assertEqual(settings.cards_per_session, 20)
        self.assertEqual(settings.default_session_duration, 20)

    def test_get_or_create_for_user(self):
        """Test de la methode get_or_create_for_user"""
        settings = RevisionSettings.get_or_create_for_user(self.user)
        
        self.assertIsInstance(settings, RevisionSettings)
        self.assertEqual(settings.user, self.user)
        
        # Verifier qu'un second appel retourne la meme instance
        settings2 = RevisionSettings.get_or_create_for_user(self.user)
        self.assertEqual(settings.id, settings2.id)

    def test_apply_preset_beginner(self):
        """Test d'application du preset debutant"""
        settings, created = RevisionSettings.objects.get_or_create(user=self.user)
        success = settings.apply_preset('beginner')
        
        self.assertTrue(success)
        settings.refresh_from_db()
        self.assertEqual(settings.default_difficulty, 'easy')
        self.assertEqual(settings.cards_per_session, 10)
        self.assertEqual(settings.default_session_duration, 15)

    def test_get_session_config(self):
        """Test de recuperation de la configuration de session"""
        settings, created = RevisionSettings.objects.get_or_create(user=self.user)
        config = settings.get_session_config()
        
        self.assertIn('study_mode', config)
        self.assertIn('difficulty', config)
        self.assertIn('session_duration', config)
        self.assertIn('cards_per_session', config)


class RevisionSessionConfigModelTest(TestCase):
    """Tests pour le modele RevisionSessionConfig"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_session_config_creation(self):
        """Test de creation d'une configuration de session"""
        config = RevisionSessionConfig.objects.create(
            user=self.user,
            name="Session rapide",
            session_type="quick",
            duration_minutes=15,
            target_cards=10
        )
        
        self.assertEqual(config.user, self.user)
        self.assertEqual(config.name, "Session rapide")
        self.assertEqual(config.session_type, "quick")
        self.assertTrue(config.include_new_cards)
        self.assertTrue(config.include_review_cards)


class RevisionSettingsAPITest(APITestCase):
    """Tests pour l'API des parametres de revision"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_revision_settings(self):
        """Test de recuperation des parametres de revision"""
        url = '/api/v1/revision/settings/api/settings/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('default_study_mode', response.data)
        self.assertIn('preset_options', response.data)

    def test_update_revision_settings(self):
        """Test de mise a jour des parametres"""
        url = '/api/v1/revision/settings/api/settings/1/'
        data = {
            'cards_per_session': 15,
            'default_session_duration': 25
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cards_per_session'], 15)
        self.assertEqual(response.data['default_session_duration'], 25)

    def test_apply_preset(self):
        """Test d'application d'un preset"""
        url = '/api/v1/revision/settings/api/settings/apply_preset/'
        data = {'preset_name': 'intermediate'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['preset_applied'], 'intermediate')

    def test_get_stats(self):
        """Test de recuperation des statistiques"""
        # First create some test data
        from apps.revision.models.revision_flashcard import FlashcardDeck, Flashcard
        
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Test Deck',
            description='Test deck for stats'
        )
        
        Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Test question',
            back_text='Test answer'
        )
        
        url = '/api/v1/revision/settings/api/settings/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_cards', response.data)
        self.assertIn('cards_learned', response.data)