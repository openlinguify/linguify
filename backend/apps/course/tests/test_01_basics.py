"""
Tests simples pour vérifier la configuration Django TestCase
Conversion de test_exercises_simple.py vers Django TestCase
"""

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CourseBasicsTests(TestCase):
    """Tests simples pour vérifier la configuration Django"""
    
    def test_django_db_setup(self):
        """Test simple pour vérifier que la connexion à la base de données fonctionne"""
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Vérifier que l'utilisateur a été créé
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # Vérifier que l'utilisateur existe toujours
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
        
        # Nettoyage optionnel (pas de suppression pour éviter les conflits de relations)
        # user.delete()
    
    def test_timezone_awareness(self):
        """Test pour vérifier que les dates sont gérées avec la sensibilité au fuseau horaire"""
        now = timezone.now()
        self.assertIsNotNone(now.tzinfo)
        
        # Vérifier qu'une date future est bien dans le futur
        future = now + timezone.timedelta(days=30)
        self.assertGreater(future, now)
        
        # Vérifier que la différence est de 30 jours
        diff = future - now
        self.assertEqual(diff.days, 30)
    
    def test_model_imports(self):
        """Test pour vérifier que les modèles peuvent être importés correctement"""
        from apps.course.models import Unit, Lesson, ContentLesson
        
        # Vérifier que les classes sont bien des classes Django Model
        self.assertTrue(hasattr(Unit, 'objects'))
        self.assertTrue(hasattr(Lesson, 'objects'))
        self.assertTrue(hasattr(ContentLesson, 'objects'))
    
    def test_basic_model_creation(self):
        """Test de création basique de modèles sans erreurs"""
        from apps.course.models import Unit
        
        # Créer une unité simple
        unit = Unit.objects.create(
            title_en="Test Unit",
            title_fr="Unité Test",
            title_es="Unidad Test",
            title_nl="Test Eenheid",
            level="A1",
            order=1
        )
        
        # Vérifier que l'unité a été créée
        self.assertIsNotNone(unit.id)
        self.assertEqual(unit.level, "A1")
        self.assertEqual(unit.order, 1)
        
        # Vérifier la représentation string
        str_repr = str(unit)
        self.assertIn("Test Unit", str_repr)
        self.assertIn("A1", str_repr)
    
    def test_model_validation(self):
        """Test de validation des modèles"""
        from apps.course.models import Unit
        
        # Test avec des données valides
        unit = Unit(
            title_en="Valid Unit",
            title_fr="Unité Valide",
            title_es="Unidad Válida",
            title_nl="Geldige Eenheid",
            level="B1",
            order=5
        )
        
        # La validation ne devrait pas lever d'erreur
        try:
            unit.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")
        
        # Sauvegarder sans erreur
        unit.save()
        self.assertIsNotNone(unit.id)
    
    def test_model_relationships(self):
        """Test des relations entre modèles"""
        from apps.course.models import Unit, Lesson
        
        # Créer une unité
        unit = Unit.objects.create(
            title_en="Relationship Test Unit",
            title_fr="Unité Test Relations",
            title_es="Unidad Test Relaciones",
            title_nl="Relatie Test Eenheid",
            level="B2",
            order=1
        )
        
        # Créer une leçon liée à l'unité
        lesson = Lesson.objects.create(
            title_en="Test Lesson",
            title_fr="Leçon Test",
            title_es="Lección Test",
            title_nl="Test Les",
            order=1,
            unit=unit,
            lesson_type='theory'
        )
        
        # Vérifier la relation
        self.assertEqual(lesson.unit, unit)
        self.assertIn(lesson, unit.lessons.all())
        
        # Vérifier le comptage
        self.assertEqual(unit.lessons.count(), 1)
    
    def test_multilingual_fields(self):
        """Test des champs multilingues"""
        from apps.course.models import Unit
        
        unit = Unit.objects.create(
            title_en="English Title",
            title_fr="Titre Français",
            title_es="Título Español",
            title_nl="Nederlandse Titel",
            level="C1",
            order=1
        )
        
        # Vérifier que tous les champs sont bien enregistrés
        self.assertEqual(unit.title_en, "English Title")
        self.assertEqual(unit.title_fr, "Titre Français")
        self.assertEqual(unit.title_es, "Título Español")
        self.assertEqual(unit.title_nl, "Nederlandse Titel")
        
        # Vérifier les méthodes de récupération si elles existent
        if hasattr(unit, 'get_unit_title'):
            self.assertEqual(unit.get_unit_title('en'), "English Title")
            self.assertEqual(unit.get_unit_title('fr'), "Titre Français")
            self.assertEqual(unit.get_unit_title('es'), "Título Español")
            self.assertEqual(unit.get_unit_title('nl'), "Nederlandse Titel")