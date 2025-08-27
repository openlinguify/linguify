from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import LanguagelearningItem

User = get_user_model()


class LanguagelearningTestCase(TestCase):
    """Tests pour l'app Language Learning"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_item(self):
        """Test de création d'un item"""
        item = LanguagelearningItem.objects.create(
            user=self.user,
            title='Test Item',
            description='Test description'
        )
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.user, self.user)
        self.assertTrue(item.is_active)
    
    def test_home_view(self):
        """Test de la vue d'accueil"""
        response = self.client.get('/language-learning/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Language Learning')
    
    def test_create_view(self):
        """Test de la vue de création"""
        response = self.client.post('/language-learning/create/', {
            'title': 'New Item',
            'description': 'New description',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect après création
        self.assertTrue(LanguagelearningItem.objects.filter(title='New Item').exists())
    
    def test_api_items(self):
        """Test de l'API items"""
        LanguagelearningItem.objects.create(
            user=self.user,
            title='API Test Item',
            description='API test description'
        )
        
        response = self.client.get('/language-learning/api/items/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['items'][0]['title'], 'API Test Item')
