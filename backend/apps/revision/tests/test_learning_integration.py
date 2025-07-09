# backend/apps/revision/tests/test_learning_integration.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.revision.models import FlashcardDeck, Flashcard

User = get_user_model()


class LearningSettingsIntegrationTest(TestCase):
    """Tests d'intégration pour le système complet de paramétrage d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_complete_learning_workflow_normal_preset(self):
        """Test d'un workflow complet d'apprentissage avec preset normal"""
        # Créer un deck avec le preset "normal"
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Normal Learning Deck',
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        # Créer des cartes
        cards = []
        for i in range(5):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Question {i+1}',
                back_text=f'Answer {i+1}'
            )
            cards.append(card)
        
        # Simuler une session d'étude réaliste
        
        # Étape 1: Première révision - quelques erreurs
        for i, card in enumerate(cards):
            if i < 3:  # 3 premières cartes correctes
                card.update_review_progress(is_correct=True)
            else:  # 2 dernières incorrectes
                card.update_review_progress(is_correct=False)
        
        # Vérifier l'état après première révision
        learned_count = Flashcard.objects.filter(deck=deck, learned=True).count()
        self.assertEqual(learned_count, 0)  # Aucune carte apprise encore
        
        # Étape 2: Deuxième révision - amélioration
        for card in cards:
            card.update_review_progress(is_correct=True)
        
        # Vérifier l'état après deuxième révision
        learned_count = Flashcard.objects.filter(deck=deck, learned=True).count()
        self.assertEqual(learned_count, 0)  # Toujours pas apprises (besoin de 3)
        
        # Étape 3: Troisième révision - maîtrise
        for card in cards:
            card.update_review_progress(is_correct=True)
        
        # Vérifier l'état final
        for card in cards:
            card.refresh_from_db()
        
        # Les 3 premières cartes devraient être apprises (3 révisions correctes)
        self.assertTrue(cards[0].learned)
        self.assertTrue(cards[1].learned)
        self.assertTrue(cards[2].learned)
        self.assertEqual(cards[0].correct_reviews_count, 3)
        
        # Les 2 dernières ont 1 erreur puis 2 correctes = 2 correctes seulement
        self.assertFalse(cards[3].learned)
        self.assertFalse(cards[4].learned)
        self.assertEqual(cards[3].correct_reviews_count, 2)
        self.assertEqual(cards[4].correct_reviews_count, 2)

    def test_intensive_learning_with_reset(self):
        """Test apprentissage intensif avec reset sur erreur"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Intensive Deck',
            required_reviews_to_learn=5,
            auto_mark_learned=True,
            reset_on_wrong_answer=True
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Difficult concept',
            back_text='Complex answer'
        )
        
        # Scenario: progression puis erreur qui remet à zéro
        
        # 4 révisions correctes
        for _ in range(4):
            card.update_review_progress(is_correct=True)
        
        self.assertEqual(card.correct_reviews_count, 4)
        self.assertFalse(card.learned)  # Pas encore apprise (besoin de 5)
        
        # Erreur -> reset
        card.update_review_progress(is_correct=False)
        
        self.assertEqual(card.correct_reviews_count, 0)  # Reset!
        self.assertEqual(card.total_reviews_count, 5)
        self.assertFalse(card.learned)
        
        # Recommencer - 5 révisions correctes d'affilée
        for _ in range(5):
            card.update_review_progress(is_correct=True)
        
        self.assertTrue(card.learned)
        self.assertEqual(card.correct_reviews_count, 5)
        self.assertEqual(card.total_reviews_count, 10)

    def test_manual_learning_control(self):
        """Test contrôle manuel de l'apprentissage (auto_mark_learned=False)"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Manual Control Deck',
            required_reviews_to_learn=2,
            auto_mark_learned=False,  # Pas de marquage automatique
            reset_on_wrong_answer=False
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Manual card',
            back_text='Manual answer'
        )
        
        # Même avec 5 révisions correctes, pas de marquage automatique
        for _ in range(5):
            card.update_review_progress(is_correct=True)
        
        self.assertEqual(card.correct_reviews_count, 5)
        self.assertFalse(card.learned)  # Pas marquée automatiquement
        
        # Marquage manuel nécessaire
        card.learned = True
        card.save()
        
        self.assertTrue(card.learned)

    def test_preset_application_and_recalculation(self):
        """Test application d'un preset et recalcul des statuts"""
        # Créer un deck avec paramètres initiaux
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Preset Test Deck',
            required_reviews_to_learn=2,  # Facile initialement
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        # Créer des cartes et les faire progresser
        cards = []
        for i in range(3):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Card {i+1}',
                back_text=f'Answer {i+1}'
            )
            
            # 2 révisions correctes -> apprise avec paramètres initiaux
            card.update_review_progress(is_correct=True)
            card.update_review_progress(is_correct=True)
            
            cards.append(card)
        
        # Vérifier que toutes sont apprises
        for card in cards:
            card.refresh_from_db()
            self.assertTrue(card.learned)
        
        # Changer pour preset expert (5 révisions requises)
        deck.required_reviews_to_learn = 5
        deck.save()
        
        # Recalculer les statuts
        deck.recalculate_cards_learned_status()
        
        # Maintenant aucune carte ne devrait être apprise (2 < 5)
        for card in cards:
            card.refresh_from_db()
            self.assertFalse(card.learned)
            self.assertEqual(card.correct_reviews_count, 2)

    def test_mixed_performance_scenario(self):
        """Test scénario réaliste avec performance mixte"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Mixed Performance Deck',
            required_reviews_to_learn=3,
            auto_mark_learned=True,
            reset_on_wrong_answer=False
        )
        
        # Différents types de cartes
        easy_card = Flashcard.objects.create(
            user=self.user, deck=deck,
            front_text='Easy card', back_text='Easy answer'
        )
        
        medium_card = Flashcard.objects.create(
            user=self.user, deck=deck,
            front_text='Medium card', back_text='Medium answer'
        )
        
        hard_card = Flashcard.objects.create(
            user=self.user, deck=deck,
            front_text='Hard card', back_text='Hard answer'
        )
        
        # Simulation de performance réaliste
        
        # Carte facile: 3 bonnes réponses directement
        for _ in range(3):
            easy_card.update_review_progress(is_correct=True)
        
        # Carte moyenne: alternance réussites/échecs
        medium_card.update_review_progress(is_correct=True)   # 1
        medium_card.update_review_progress(is_correct=False)  # toujours 1
        medium_card.update_review_progress(is_correct=True)   # 2
        medium_card.update_review_progress(is_correct=True)   # 3
        
        # Carte difficile: beaucoup d'erreurs
        for _ in range(5):
            hard_card.update_review_progress(is_correct=False)
        hard_card.update_review_progress(is_correct=True)     # 1
        hard_card.update_review_progress(is_correct=False)    # toujours 1
        hard_card.update_review_progress(is_correct=True)     # 2
        
        # Vérifier les résultats
        easy_card.refresh_from_db()
        medium_card.refresh_from_db()
        hard_card.refresh_from_db()
        
        self.assertTrue(easy_card.learned)
        self.assertEqual(easy_card.correct_reviews_count, 3)
        self.assertEqual(easy_card.total_reviews_count, 3)
        
        self.assertTrue(medium_card.learned)
        self.assertEqual(medium_card.correct_reviews_count, 3)
        self.assertEqual(medium_card.total_reviews_count, 4)
        
        self.assertFalse(hard_card.learned)
        self.assertEqual(hard_card.correct_reviews_count, 2)
        self.assertEqual(hard_card.total_reviews_count, 8)
        
        # Vérifier les statistiques du deck
        stats = deck.get_learning_statistics()
        self.assertEqual(stats['total_cards'], 3)
        self.assertEqual(stats['learned_cards'], 2)
        self.assertEqual(stats['cards_needing_review'], 1)

    def test_different_presets_comparison(self):
        """Test comparaison de différents presets"""
        presets_configs = [
            ('beginner', 1, True, False),
            ('normal', 3, True, False),
            ('intensive', 5, True, False),
            ('expert', 7, True, True)
        ]
        
        results = {}
        
        for preset_name, required_reviews, auto_mark, reset_wrong in presets_configs:
            deck = FlashcardDeck.objects.create(
                user=self.user,
                name=f'{preset_name.title()} Deck',
                required_reviews_to_learn=required_reviews,
                auto_mark_learned=auto_mark,
                reset_on_wrong_answer=reset_wrong
            )
            
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'{preset_name} question',
                back_text=f'{preset_name} answer'
            )
            
            # Simuler 3 révisions correctes
            for _ in range(3):
                card.update_review_progress(is_correct=True)
            
            card.refresh_from_db()
            results[preset_name] = {
                'learned': card.learned,
                'reviews_needed': required_reviews,
                'progress_pct': card.learning_progress_percentage
            }
        
        # Vérifier les résultats
        self.assertTrue(results['beginner']['learned'])    # 1 révision suffisante
        self.assertTrue(results['normal']['learned'])      # 3 révisions exactes
        self.assertFalse(results['intensive']['learned'])  # 5 révisions nécessaires
        self.assertFalse(results['expert']['learned'])     # 7 révisions nécessaires
        
        # Vérifier les pourcentages de progression
        self.assertEqual(results['beginner']['progress_pct'], 100)
        self.assertEqual(results['normal']['progress_pct'], 100)
        self.assertEqual(results['intensive']['progress_pct'], 60)  # 3/5 * 100
        self.assertAlmostEqual(results['expert']['progress_pct'], 42.86, places=1)  # 3/7 * 100

    def test_learning_statistics_comprehensive(self):
        """Test complet des statistiques d'apprentissage"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Statistics Test Deck',
            required_reviews_to_learn=4
        )
        
        # Créer 10 cartes avec différents états
        cards_data = [
            (4, 4, True),   # Apprise
            (4, 5, True),   # Apprise 
            (3, 6, False),  # 75% de progression
            (2, 3, False),  # 50% de progression
            (1, 4, False),  # 25% de progression
            (0, 2, False),  # 0% de progression
            (0, 0, False),  # Jamais révisée
            (3, 3, False),  # 75% de progression
            (4, 8, True),   # Apprise avec beaucoup de révisions
            (1, 1, False),  # 25% de progression
        ]
        
        for i, (correct, total, learned) in enumerate(cards_data):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Card {i+1}',
                back_text=f'Answer {i+1}',
                correct_reviews_count=correct,
                total_reviews_count=total,
                learned=learned
            )
        
        # Obtenir les statistiques
        stats = deck.get_learning_statistics()
        
        self.assertEqual(stats['total_cards'], 10)
        self.assertEqual(stats['learned_cards'], 3)
        self.assertEqual(stats['cards_needing_review'], 7)
        
        # Calculer la progression moyenne attendue
        # (100 + 100 + 75 + 50 + 25 + 0 + 0 + 75 + 100 + 25) / 10 = 55%
        expected_avg = (100 + 100 + 75 + 50 + 25 + 0 + 0 + 75 + 100 + 25) / 10
        self.assertEqual(stats['average_progress'], expected_avg)

    def test_edge_cases(self):
        """Test des cas limites"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Edge Cases Deck',
            required_reviews_to_learn=1,  # Minimum
            auto_mark_learned=True,
            reset_on_wrong_answer=True
        )
        
        card = Flashcard.objects.create(
            user=self.user,
            deck=deck,
            front_text='Edge case card',
            back_text='Edge case answer'
        )
        
        # Test: 1 révision requise seulement
        card.update_review_progress(is_correct=True)
        self.assertTrue(card.learned)
        
        # Test: Carte déjà apprise, erreur avec reset
        card.update_review_progress(is_correct=False)
        # Avec reset, même une carte apprise peut redevenir non-apprise
        self.assertFalse(card.learned)
        self.assertEqual(card.correct_reviews_count, 0)
        
        # Test: Division par zéro évitée
        deck.required_reviews_to_learn = 0  # Cas impossible normalement
        deck.save()
        
        # Ne devrait pas lever d'exception
        try:
            progress = card.learning_progress_percentage
            remaining = card.reviews_remaining_to_learn
            self.assertIsInstance(progress, (int, float))
            self.assertIsInstance(remaining, int)
        except ZeroDivisionError:
            self.fail("Division par zéro non gérée")


class LearningSettingsPerformanceTest(TestCase):
    """Tests de performance pour le système d'apprentissage"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123'
        )

    def test_bulk_progress_update_performance(self):
        """Test performance des mises à jour en masse"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Performance Test Deck',
            required_reviews_to_learn=3
        )
        
        # Créer beaucoup de cartes
        cards = []
        for i in range(100):
            card = Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Performance card {i+1}',
                back_text=f'Performance answer {i+1}'
            )
            cards.append(card)
        
        # Mesurer le temps de mise à jour en masse
        start_time = timezone.now()
        
        # Simuler une session d'étude sur toutes les cartes
        for card in cards:
            card.update_review_progress(is_correct=True)
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # La mise à jour de 100 cartes devrait prendre moins de 5 secondes
        self.assertLess(duration, 5.0, f"Bulk update took {duration}s, too slow")
        
        # Vérifier que tout fonctionne correctement
        learned_count = Flashcard.objects.filter(deck=deck, learned=False).count()
        self.assertEqual(learned_count, 100)  # Pas encore apprises (1/3 révisions)

    def test_statistics_calculation_performance(self):
        """Test performance du calcul des statistiques"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name='Stats Performance Test',
            required_reviews_to_learn=5
        )
        
        # Créer beaucoup de cartes avec états variés
        for i in range(200):
            Flashcard.objects.create(
                user=self.user,
                deck=deck,
                front_text=f'Stats card {i+1}',
                back_text=f'Stats answer {i+1}',
                correct_reviews_count=i % 6,  # 0 à 5
                total_reviews_count=(i % 6) + (i % 3),
                learned=(i % 6) >= 5
            )
        
        # Mesurer le temps de calcul des statistiques
        start_time = timezone.now()
        
        stats = deck.get_learning_statistics()
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # Le calcul des stats sur 200 cartes devrait être rapide
        self.assertLess(duration, 1.0, f"Statistics calculation took {duration}s, too slow")
        
        # Vérifier la cohérence des résultats
        self.assertEqual(stats['total_cards'], 200)
        self.assertIsInstance(stats['learned_cards'], int)
        self.assertIsInstance(stats['average_progress'], (int, float))