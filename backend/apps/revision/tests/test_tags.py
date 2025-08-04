# Tests spécifiques pour le système de tags de l'app révision

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from apps.revision.models import FlashcardDeck, Flashcard
from apps.revision.serializers import FlashcardDeckSerializer, FlashcardDeckCreateSerializer
from apps.revision.views.flashcard_views import TagsAPIView
import json
import re

User = get_user_model()

class TagsModelTest(TestCase):
    """Tests pour le système de tags au niveau du modèle"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_deck_with_empty_tags(self):
        """Test d'un deck avec des tags vides"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Empty Tags Deck",
            tags=[]
        )
        
        self.assertEqual(deck.tags, [])
        self.assertIsInstance(deck.tags, list)
    
    def test_deck_with_single_tag(self):
        """Test d'un deck avec un seul tag"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Single Tag Deck",
            tags=['python']
        )
        
        self.assertEqual(deck.tags, ['python'])
        self.assertEqual(len(deck.tags), 1)
    
    def test_deck_with_multiple_tags(self):
        """Test d'un deck avec plusieurs tags"""
        tags = ['python', 'django', 'web', 'backend']
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Multiple Tags Deck",
            tags=tags
        )
        
        self.assertEqual(deck.tags, tags)
        self.assertEqual(len(deck.tags), 4)
    
    def test_deck_tags_update(self):
        """Test de mise à jour des tags d'un deck"""
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Update Tags Deck",
            tags=['old', 'tags']
        )
        
        # Mettre à jour les tags
        deck.tags = ['new', 'updated', 'tags']
        deck.save()
        
        # Recharger depuis la base
        deck.refresh_from_db()
        self.assertEqual(deck.tags, ['new', 'updated', 'tags'])
    
    def test_deck_tags_json_serialization(self):
        """Test de sérialisation JSON des tags"""
        tags = ['python', 'django', 'api', 'rest']
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="JSON Tags Deck",
            tags=tags
        )
        
        # Vérifier que les tags peuvent être sérialisés en JSON
        serialized = json.dumps(deck.tags)
        deserialized = json.loads(serialized)
        
        self.assertEqual(deserialized, tags)
    
    def test_deck_tags_special_characters(self):
        """Test des tags avec caractères spéciaux autorisés"""
        tags = ['c++', 'asp.net', 'node-js', 'vue_js']
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Special Chars Tags Deck",
            tags=tags
        )
        
        self.assertEqual(deck.tags, tags)
    
    def test_deck_tags_case_sensitivity(self):
        """Test de sensibilité à la casse des tags"""
        tags = ['Python', 'DJANGO', 'web', 'API']
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Case Sensitive Tags Deck",
            tags=tags
        )
        
        # Les tags doivent être stockés tels quels
        self.assertEqual(deck.tags, tags)
    
    def test_deck_tags_unicode_support(self):
        """Test du support Unicode dans les tags"""
        tags = ['français', 'español', '中文', 'العربية']
        deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Unicode Tags Deck",
            tags=tags
        )
        
        self.assertEqual(deck.tags, tags)

class TagsSerializerTest(TestCase):
    """Tests pour la validation des tags dans les serializers"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_valid_tags_validation(self):
        """Test de validation des tags valides"""
        data = {
            'name': 'Test Deck',
            'tags': ['python', 'django', 'web-dev', 'api_rest']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save(user=self.user)
        self.assertEqual(deck.tags, ['python', 'django', 'web-dev', 'api_rest'])
    
    def test_invalid_tags_validation(self):
        """Test de validation des tags invalides"""
        invalid_tags_data = [
            {'name': 'Test 1', 'tags': ['valid', 'invalid@tag!']},  # Caractères spéciaux
            {'name': 'Test 2', 'tags': ['valid', 'invalid tag with spaces']},  # Espaces
            {'name': 'Test 3', 'tags': ['valid', 'invalid#tag']},  # Caractère #
            {'name': 'Test 4', 'tags': ['valid', 'invalid%tag']},  # Caractère %
        ]
        
        for data in invalid_tags_data:
            serializer = FlashcardDeckCreateSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('tags', serializer.errors)
    
    def test_empty_tag_validation(self):
        """Test de validation des tags vides"""
        data = {
            'name': 'Test Deck',
            'tags': ['valid', '', 'another']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_duplicate_tags_cleaning(self):
        """Test du nettoyage des tags dupliqués"""
        data = {
            'name': 'Test Deck',
            'tags': ['python', 'PYTHON', 'django', 'Python', 'django']
        }
        
        # Créer un contexte request pour le serializer
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.post('/test')
        request.user = self.user
        
        serializer = FlashcardDeckCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save()
        # Les tags doivent être nettoyés et dédupliqués (case insensitive)
        self.assertEqual(len(deck.tags), 2)
        
        # Vérifier que les tags dédupliqués sont présents (case insensitive)
        tags_lower = [tag.lower() for tag in deck.tags]
        self.assertIn('python', tags_lower)
        self.assertIn('django', tags_lower)
    
    def test_max_tags_validation(self):
        """Test de validation du nombre maximum de tags"""
        data = {
            'name': 'Test Deck',
            'tags': [f'tag{i}' for i in range(11)]  # 11 tags (max 10)
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_long_tag_validation(self):
        """Test de validation de la longueur des tags"""
        data = {
            'name': 'Test Deck',
            'tags': ['valid', 'a' * 51]  # Tag de 51 caractères (max 50)
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_tags_not_list_validation(self):
        """Test de validation quand tags n'est pas une liste"""
        data = {
            'name': 'Test Deck',
            'tags': 'not-a-list'
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tags', serializer.errors)
    
    def test_tags_whitespace_cleaning(self):
        """Test du nettoyage des espaces dans les tags"""
        data = {
            'name': 'Test Deck',
            'tags': ['  python  ', '  django  ', '  web  ']
        }
        
        serializer = FlashcardDeckCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        deck = serializer.save(user=self.user)
        # Les espaces doivent être supprimés
        self.assertEqual(deck.tags, ['python', 'django', 'web'])

class TagsAPITest(APITestCase):
    """Tests pour l'API des tags"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des decks avec des tags
        self.deck1 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 1",
            tags=['python', 'django', 'web']
        )
        
        self.deck2 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 2",
            tags=['javascript', 'react', 'web']
        )
        
        self.deck3 = FlashcardDeck.objects.create(
            user=self.user,
            name="Deck 3",
            tags=['java', 'spring']
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_all_tags(self):
        """Test de récupération de tous les tags"""
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
        self.assertIn('count', response.data)
        
        # Vérifier que tous les tags uniques sont présents
        expected_tags = ['django', 'java', 'javascript', 'python', 'react', 'spring', 'web']
        self.assertEqual(sorted(response.data['tags']), expected_tags)
        self.assertEqual(response.data['count'], 7)
    
    def test_get_tags_with_counts(self):
        """Test de récupération des tags avec leurs comptages"""
        url = reverse('revision:tags-api')
        response = self.client.get(url, {'include_counts': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags_with_counts', response.data)
        
        # Vérifier que les comptages sont corrects
        tags_with_counts = response.data['tags_with_counts']
        web_count = next(item['count'] for item in tags_with_counts if item['tag'] == 'web')
        self.assertEqual(web_count, 2)  # 'web' apparaît dans 2 decks
    
    def test_validate_valid_tag(self):
        """Test de validation d'un tag valide"""
        url = reverse('revision:tags-api')
        data = {'tag': 'new-valid-tag'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tag'], 'new-valid-tag')
        self.assertIn('Tag validé avec succès', response.data['message'])
    
    def test_validate_invalid_tag(self):
        """Test de validation d'un tag invalide"""
        invalid_tags = [
            'invalid@tag!',
            'invalid tag with spaces',
            'invalid#tag',
            'invalid%tag',
            '',  # Tag vide
            'a' * 51,  # Tag trop long
        ]
        
        url = reverse('revision:tags-api')
        
        for invalid_tag in invalid_tags:
            data = {'tag': invalid_tag}
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('detail', response.data)
    
    def test_validate_duplicate_tag_case_insensitive(self):
        """Test de validation d'un tag dupliqué (case-insensitive)"""
        url = reverse('revision:tags-api')
        
        # Le deck1 a déjà le tag 'python' (minuscule)
        test_cases = [
            'Python',   # Majuscule
            'PYTHON',   # Tout en majuscule
            'PyThOn',   # Mixte
            'python',   # Identique
            '  python  ', # Avec espaces
        ]
        
        for duplicate_tag in test_cases:
            data = {'tag': duplicate_tag}
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('existe déjà', response.data['detail'].lower())
            self.assertIn('python', response.data['detail'].lower())
    
    def test_validate_new_tag_case_insensitive(self):
        """Test de validation d'un nouveau tag unique"""
        url = reverse('revision:tags-api')
        
        # Ce tag n'existe pas encore
        data = {'tag': 'rust'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tag'], 'rust')
        self.assertIn('validé avec succès', response.data['message'])
    
    def test_get_tags_deduplication_case_insensitive(self):
        """Test de déduplication case-insensitive dans GET /tags/"""
        # Ajouter un deck avec des tags en majuscules
        FlashcardDeck.objects.create(
            user=self.user,
            name="Uppercase Deck",
            tags=['PYTHON', 'DJANGO', 'MySQL']  # Même tags mais différente casse
        )
        
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il n'y a pas de doublons case-insensitive
        tags = response.data['tags']
        tags_lower = [tag.lower() for tag in tags]
        
        # Pas de doublons après normalisation
        self.assertEqual(len(tags_lower), len(set(tags_lower)))
        
        # Vérifier que 'python' n'apparaît qu'une fois (peu importe la casse)
        python_variations = [tag for tag in tags if tag.lower() == 'python']
        self.assertEqual(len(python_variations), 1)
    
    def test_search_tags(self):
        """Test de recherche dans les tags"""
        url = reverse('revision:tags-api')
        response = self.client.get(url, {'search': 'java'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Devrait retourner 'java' et 'javascript'
        found_tags = response.data['tags']
        self.assertIn('java', found_tags)
        self.assertIn('javascript', found_tags)
        self.assertNotIn('python', found_tags)
    
    def test_tags_authentication_required(self):
        """Test que l'authentification est requise"""
        self.client.force_authenticate(user=None)
        url = reverse('revision:tags-api')
        
        response = self.client.get(url)
        # API peut retourner 401 ou 403 selon la configuration DRF
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_tags_isolation_between_users(self):
        """Test que les tags sont isolés entre utilisateurs"""
        # Créer un autre utilisateur avec des tags différents
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        FlashcardDeck.objects.create(
            user=user2,
            name="User2 Deck",
            tags=['php', 'laravel']
        )
        
        # Authentifier user1
        self.client.force_authenticate(user=self.user)
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        # User1 ne devrait voir que ses propres tags
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user1_tags = response.data['tags']
        self.assertNotIn('php', user1_tags)
        self.assertNotIn('laravel', user1_tags)
        self.assertIn('python', user1_tags)
        
        # Authentifier user2
        self.client.force_authenticate(user=user2)
        response = self.client.get(url)
        
        # User2 ne devrait voir que ses propres tags
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user2_tags = response.data['tags']
        self.assertIn('php', user2_tags)
        self.assertIn('laravel', user2_tags)
        self.assertNotIn('python', user2_tags)

class TagsFilteringTest(APITestCase):
    """Tests pour le filtrage par tags"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des decks avec des tags spécifiques
        self.python_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Python Deck",
            tags=['python', 'programming']
        )
        
        self.web_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Web Deck",
            tags=['javascript', 'web', 'frontend']
        )
        
        self.mixed_deck = FlashcardDeck.objects.create(
            user=self.user,
            name="Mixed Deck",
            tags=['python', 'web', 'fullstack']
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_deck_list_includes_tags(self):
        """Test que la liste des decks inclut les tags"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que chaque deck a ses tags
        decks = response.data['results']
        for deck in decks:
            self.assertIn('tags', deck)
            self.assertIsInstance(deck['tags'], list)
    
    def test_client_side_tag_filtering(self):
        """Test du filtrage côté client par tags"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Simuler le filtrage côté client
        all_decks = response.data['results']
        
        # Filtrer les decks avec le tag 'python'
        python_decks = [d for d in all_decks if 'python' in d['tags']]
        self.assertEqual(len(python_decks), 2)  # python_deck et mixed_deck
        
        # Filtrer les decks avec le tag 'web'
        web_decks = [d for d in all_decks if 'web' in d['tags']]
        self.assertEqual(len(web_decks), 2)  # web_deck et mixed_deck
        
        # Filtrer les decks avec le tag 'frontend'
        frontend_decks = [d for d in all_decks if 'frontend' in d['tags']]
        self.assertEqual(len(frontend_decks), 1)  # Seulement web_deck
    
    def test_multi_tag_filtering_or_logic(self):
        """Test du filtrage multi-tags avec logique OR (au moins un tag)"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        all_decks = response.data['results']
        
        # Simuler le filtrage JavaScript avec logique OR
        def filter_decks_by_tags_or(decks, selected_tags):
            """Réplique de la fonction JS avec logique OR"""
            if not selected_tags:
                return decks
            
            return [deck for deck in decks 
                   if deck['tags'] and 
                   any(selected_tag.lower() in [tag.lower() for tag in deck['tags']] 
                       for selected_tag in selected_tags)]
        
        # Test 1: Tags qui n'ont aucun deck en commun
        # 'frontend' (seulement web_deck) + 'programming' (seulement python_deck)
        selected_tags = ['frontend', 'programming']
        filtered = filter_decks_by_tags_or(all_decks, selected_tags)
        
        # Avec OR logic: devrait inclure web_deck ET python_deck
        self.assertEqual(len(filtered), 2)
        deck_names = [d['name'] for d in filtered]
        self.assertIn('Web Deck', deck_names)
        self.assertIn('Python Deck', deck_names)
        
        # Test 2: Tags qui ont des decks en commun
        # 'python' + 'web' (mixed_deck a les deux)
        selected_tags = ['python', 'web']
        filtered = filter_decks_by_tags_or(all_decks, selected_tags)
        
        # Avec OR logic: python_deck, web_deck, mixed_deck (tous)
        self.assertEqual(len(filtered), 3)
        
        # Test 3: Un seul tag
        selected_tags = ['fullstack']
        filtered = filter_decks_by_tags_or(all_decks, selected_tags)
        
        # Seulement mixed_deck a ce tag
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['name'], 'Mixed Deck')
    
    def test_multi_tag_filtering_case_insensitive(self):
        """Test du filtrage multi-tags case-insensitive"""
        url = reverse('revision:deck-list')
        response = self.client.get(url)
        
        all_decks = response.data['results']
        
        def filter_decks_by_tags_case_insensitive(decks, selected_tags):
            """Réplique de la fonction JS avec normalisation case-insensitive"""
            if not selected_tags:
                return decks
            
            return [deck for deck in decks 
                   if deck['tags'] and 
                   any(selected_tag.strip().lower() == deck_tag.strip().lower()
                       for selected_tag in selected_tags
                       for deck_tag in deck['tags'])]
        
        # Test avec différentes casses
        test_cases = [
            ['PYTHON'],      # Majuscule
            ['Python'],      # Première lettre majuscule  
            ['python'],      # Minuscule
            ['  python  '],  # Avec espaces
        ]
        
        for selected_tags in test_cases:
            filtered = filter_decks_by_tags_case_insensitive(all_decks, selected_tags)
            
            # Tous devraient retourner les mêmes decks avec 'python'
            self.assertEqual(len(filtered), 2)  # python_deck et mixed_deck
            deck_names = [d['name'] for d in filtered]
            self.assertIn('Python Deck', deck_names)
            self.assertIn('Mixed Deck', deck_names)
    
    def test_search_by_tag_content(self):
        """Test de recherche par contenu de tags"""
        url = reverse('revision:deck-list')
        
        # Rechercher 'python' (devrait matcher les decks avec ce tag)
        response = self.client.get(url, {'search': 'python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # La recherche devrait inclure les decks avec 'python' dans le nom ou les tags
        found_decks = response.data['results']
        deck_names = [d['name'] for d in found_decks]
        
        # Le deck "Python Deck" devrait être trouvé par nom
        self.assertIn('Python Deck', deck_names)

class TagsEdgeCasesTest(APITestCase):
    """Tests des cas limites pour les tags"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_deck_without_tags(self):
        """Test d'un deck sans tags"""
        deck_data = {
            'name': 'No Tags Deck',
            'description': 'Deck without tags'
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], [])
    
    def test_deck_with_null_tags(self):
        """Test d'un deck avec tags null"""
        deck_data = {
            'name': 'Null Tags Deck',
            'tags': None
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        # Devrait être converti en liste vide
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], [])
    
    def test_very_long_tag_name(self):
        """Test d'un tag très long"""
        long_tag = 'a' * 100  # 100 caractères
        
        deck_data = {
            'name': 'Long Tag Deck',
            'tags': [long_tag]
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tags', response.data)
    
    def test_special_unicode_tags(self):
        """Test de tags avec caractères Unicode spéciaux"""
        unicode_tags = ['🐍python', '⚡️javascript', '🔥django']
        
        deck_data = {
            'name': 'Unicode Tags Deck',
            'tags': unicode_tags
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], unicode_tags)
    
    def test_tags_with_numbers(self):
        """Test de tags avec des numéros"""
        number_tags = ['python3', 'vue2', 'angular15', 'nodejs18']
        
        deck_data = {
            'name': 'Number Tags Deck',
            'tags': number_tags
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], number_tags)
    
    def test_empty_tags_list(self):
        """Test d'une liste de tags vide"""
        deck_data = {
            'name': 'Empty Tags List Deck',
            'tags': []
        }
        
        url = reverse('revision:deck-list')
        response = self.client.post(url, deck_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tags'], [])
    
    def test_tags_api_with_no_decks(self):
        """Test de l'API tags sans decks"""
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tags'], [])
        self.assertEqual(response.data['count'], 0)

class TagsPerformanceTest(APITestCase):
    """Tests de performance pour les tags"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_many_tags_performance(self):
        """Test de performance avec beaucoup de tags"""
        # Créer 50 decks avec des tags variés
        for i in range(50):
            FlashcardDeck.objects.create(
                user=self.user,
                name=f"Deck {i}",
                tags=[f"tag{j}" for j in range(i % 10)]  # 0 à 9 tags par deck
            )
        
        # Tester les performances de l'API tags
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tags', response.data)
        self.assertGreater(len(response.data['tags']), 0)
    
    def test_duplicate_tags_performance(self):
        """Test de performance avec beaucoup de tags dupliqués"""
        # Créer 100 decks avec les mêmes tags
        common_tags = ['python', 'javascript', 'web', 'api']
        
        for i in range(100):
            FlashcardDeck.objects.create(
                user=self.user,
                name=f"Deck {i}",
                tags=common_tags
            )
        
        # Tester les performances de l'API tags
        url = reverse('revision:tags-api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tags']), 4)  # Seulement les tags uniques
        self.assertEqual(response.data['count'], 4)