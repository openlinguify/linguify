# authentication/tests/test_middleware.py
from django.test import TestCase, RequestFactory, SimpleTestCase, TransactionTestCase
from unittest.mock import patch, Mock, MagicMock
import jwt
import json
import sys
from django.contrib.auth import get_user_model
from authentication.middleware import JWTMiddleware, get_user_info

# Forcer l'utilisation de SQLite en mémoire pour tous les tests
if 'test' in sys.argv:
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

User = get_user_model()

class JWTMiddlewareTests(SimpleTestCase):
    """Tests pour le middleware JWT qui ne nécessitent pas de base de données"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Préparer un token JWT de test
        self.test_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3Qta2lkIn0.eyJpc3MiOiJodHRwczovL2Rldi03cWUyNzVvODMxZWJraGJqLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjFlZDg4NzcxNmMxZjAwMTlmMDM4YWYiLCJhdWQiOlsiaHR0cHM6Ly9saW5ndWlmeS1hcGkiLCJodHRwczovL2Rldi03cWUyNzVvODMxZWJraGJqLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTgzMjYwMDAsImV4cCI6MTYxODQxMjQwMCwiYXpwIjoiY3ROdDA3cWFVckhSbld0SGtYb0E3UUZkM2pvZHBYTnUiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIn0.signature"
        
        # Créer le middleware
        self.middleware = JWTMiddleware(lambda request: request)
        
        # Mock pour le JWKS (JSON Web Key Set)
        self.mock_jwks = {
            "keys": [
                {
                    "kid": "test-kid",
                    "kty": "RSA",
                    "use": "sig",
                    "n": "test-modulus",
                    "e": "AQAB"
                }
            ]
        }
    
    @patch('authentication.middleware.requests.get')
    def test_fetch_jwks(self, mock_get):
        """Test que le middleware récupère correctement les clés JWKS"""
        # Configurer le mock
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_get.return_value = mock_response
        
        # Appeler la méthode
        jwks = self.middleware.fetch_jwks()
        
        # Vérifier que la requête a été faite
        mock_get.assert_called_once_with('https://dev-7qe275o831ebkhbj.eu.auth0.com/.well-known/jwks.json')
        
        # Vérifier le résultat
        self.assertEqual(jwks, self.mock_jwks)
        
        # Appeler à nouveau pour vérifier le cache
        self.middleware.fetch_jwks()
        
        # La requête ne devrait être faite qu'une seule fois (cache)
        mock_get.assert_called_once()
    
    @patch('authentication.middleware.jwt.decode')
    @patch('authentication.middleware.jwt.get_unverified_header')
    @patch('authentication.middleware.JWTMiddleware.fetch_jwks')
    def test_authenticate_token_valid(self, mock_fetch_jwks, mock_get_header, mock_decode):
        """Test que le middleware authentifie correctement un token valide"""
        # Configurer les mocks
        mock_fetch_jwks.return_value = self.mock_jwks
        mock_get_header.return_value = {'kid': 'test-kid', 'alg': 'RS256'}
        
        expected_payload = {
            'iss': 'https://dev-7qe275o831ebkhbj.eu.auth0.com/',
            'sub': 'auth0|5f1ed88771c1f0019f038af',
            'aud': ['https://linguify-api', 'https://dev-7qe275o831ebkhbj.eu.auth0.com/userinfo'],
            'email': 'test@example.com'
        }
        mock_decode.return_value = expected_payload
        
        # Appeler la méthode
        payload = self.middleware.authenticate_token(self.test_token)
        
        # Vérifier le résultat
        self.assertEqual(payload, expected_payload)
        
        # Vérifier que jwt.decode a été appelé avec les bons paramètres
        mock_decode.assert_called_once()
        args, kwargs = mock_decode.call_args
        self.assertEqual(args[0], self.test_token)
        self.assertEqual(kwargs['algorithms'], ['RS256'])
        self.assertEqual(kwargs['audience'], 'https://linguify-api')
        self.assertEqual(kwargs['issuer'], 'https://dev-7qe275o831ebkhbj.eu.auth0.com/')
    
    @patch('authentication.middleware.jwt.get_unverified_header')
    def test_authenticate_token_invalid_kid(self, mock_get_header):
        """Test que le middleware rejette un token avec un 'kid' invalide"""
        # Configurer les mocks
        self.middleware.jwks = self.mock_jwks  # Définir directement le JWKS
        mock_get_header.return_value = {'kid': 'invalid-kid', 'alg': 'RS256'}
        
        # Appeler la méthode
        payload = self.middleware.authenticate_token(self.test_token)
        
        # Vérifier que le token est rejeté
        self.assertIsNone(payload)
    
    @patch('authentication.middleware.jwt.decode')
    @patch('authentication.middleware.jwt.get_unverified_header')
    @patch('authentication.middleware.JWTMiddleware.fetch_jwks')
    def test_authenticate_token_invalid_signature(self, mock_fetch_jwks, mock_get_header, mock_decode):
        """Test que le middleware rejette un token avec une signature invalide"""
        # Configurer les mocks
        mock_fetch_jwks.return_value = self.mock_jwks
        mock_get_header.return_value = {'kid': 'test-kid', 'alg': 'RS256'}
        mock_decode.side_effect = jwt.InvalidSignatureError("Invalid signature")
        
        # Appeler la méthode
        payload = self.middleware.authenticate_token(self.test_token)
        
        # Vérifier que le token est rejeté
        self.assertIsNone(payload)
    
    @patch('authentication.middleware.requests.get')
    def test_get_user_info_success(self, mock_get):
        """Test que la fonction get_user_info récupère correctement les informations de l'utilisateur"""
        # Configurer le mock
        mock_response = Mock()
        mock_response.status_code = 200
        user_info = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'given_name': 'Test',
            'family_name': 'User'
        }
        mock_response.json.return_value = user_info
        mock_get.return_value = mock_response
        
        # Appeler la fonction
        result = get_user_info(self.test_token)
        
        # Vérifier la requête
        mock_get.assert_called_once_with(
            'https://dev-7qe275o831ebkhbj.eu.auth0.com/userinfo',
            headers={'Authorization': f'Bearer {self.test_token}'}
        )
        
        # Vérifier le résultat
        self.assertEqual(result, user_info)
    
    @patch('authentication.middleware.requests.get')
    def test_get_user_info_failure(self, mock_get):
        """Test que la fonction get_user_info gère correctement les erreurs"""
        # Configurer le mock pour une erreur
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        # Appeler la fonction
        result = get_user_info(self.test_token)
        
        # Vérifier que la fonction retourne None en cas d'erreur
        self.assertIsNone(result)
        
    def test_middleware_call_without_token(self):
        """Test que le middleware ne modifie pas la requête sans token"""
        # Créer une requête sans token
        request = self.factory.get('/api/some-endpoint')
        request.headers = {}
        request.user = None
        
        # Appeler le middleware
        self.middleware(request)
        
        # Vérifier que l'utilisateur n'est pas associé à la requête
        self.assertIsNone(request.user)
    
    @patch('authentication.middleware.JWTMiddleware.authenticate_token')
    def test_middleware_call_with_invalid_token(self, mock_authenticate):
        """Test que le middleware ne modifie pas la requête avec un token invalide"""
        # Configurer les mocks
        mock_authenticate.return_value = None
        
        # Créer une requête
        request = self.factory.get('/api/some-endpoint')
        request.headers = {'Authorization': f'Bearer {self.test_token}'}
        request.user = None
        
        # Appeler le middleware
        response = self.middleware(request)
        
        # Vérifier que l'utilisateur n'est pas associé à la requête
        self.assertIsNone(response.user)

    @patch('authentication.middleware.get_user_info')
    @patch('authentication.middleware.JWTMiddleware.authenticate_token')
    @patch('authentication.middleware.User.objects.get_or_create')
    def test_middleware_call_with_valid_token_get_or_create(self, mock_get_or_create, mock_authenticate, mock_get_user_info):
        """Test que le middleware appelle get_or_create pour l'utilisateur"""
        # Configurer les mocks
        payload = {
            'iss': 'https://dev-7qe275o831ebkhbj.eu.auth0.com/',
            'sub': 'auth0|5f1ed88771c1f0019f038af',
            'email': 'test@example.com'
        }
        mock_authenticate.return_value = payload
        
        user_info = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'given_name': 'Test',
            'family_name': 'User'
        }
        mock_get_user_info.return_value = user_info
        
        # Mock l'utilisateur
        mock_user = Mock()
        mock_get_or_create.return_value = (mock_user, False)
        
        # Créer une requête
        request = self.factory.get('/api/some-endpoint')
        request.headers = {'Authorization': f'Bearer {self.test_token}'}
        
        # Appeler le middleware
        response = self.middleware(request)
        
        # Vérifier que get_or_create a été appelé avec les bons paramètres
        mock_get_or_create.assert_called_once_with(
            email='test@example.com', 
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Vérifier que l'utilisateur est associé à la requête
        self.assertEqual(response.user, mock_user)

    @patch('authentication.middleware.get_user_info')
    @patch('authentication.middleware.JWTMiddleware.authenticate_token')
    @patch('authentication.middleware.User.objects.get_or_create')
    def test_middleware_updates_existing_user(self, mock_get_or_create, mock_authenticate, mock_get_user_info):
        """Test que le middleware met à jour l'utilisateur si nécessaire"""
        # Configurer les mocks
        payload = {
            'iss': 'https://dev-7qe275o831ebkhbj.eu.auth0.com/',
            'sub': 'auth0|5f1ed88771c1f0019f038af',
            'email': 'test@example.com'
        }
        mock_authenticate.return_value = payload
        
        user_info = {
            'email': 'test@example.com',
            'nickname': 'updateduser',
            'given_name': 'Updated',
            'family_name': 'User'
        }
        mock_get_user_info.return_value = user_info
        
        # Mock l'utilisateur
        mock_user = Mock()
        mock_user.username = 'oldusername'
        mock_user.first_name = 'OldFirst'
        mock_user.last_name = 'OldLast'
        mock_get_or_create.return_value = (mock_user, False)
        
        # Créer une requête
        request = self.factory.get('/api/some-endpoint')
        request.headers = {'Authorization': f'Bearer {self.test_token}'}
        
        # Appeler le middleware
        self.middleware(request)
        
        # Vérifier que l'utilisateur a été mis à jour
        self.assertEqual(mock_user.username, 'updateduser')
        self.assertEqual(mock_user.first_name, 'Updated')
        self.assertEqual(mock_user.last_name, 'User')
        mock_user.save.assert_called()