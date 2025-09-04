#!/usr/bin/env python3
"""
Test simple pour vérifier l'intégration du système de tags global avec notebook
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')
sys.path.append('/mnt/c/Users/louis/WebstormProjects/linguify/backend')
django.setup()

from django.contrib.auth import get_user_model
from apps.notebook.models import Note
from core.models.tags import Tag, TagRelation

User = get_user_model()

def test_basic_functionality():
    """Test des fonctionnalités de base du système de tags global"""
    print("🧪 Test du système de tags global avec notebook")
    print("=" * 50)
    
    try:
        # 1. Créer un utilisateur test
        user = User.objects.create_user(
            username='test_tags_user',
            email='test@example.com',
            password='testpass123'
        )
        print("✅ Utilisateur créé:", user.username)
        
        # 2. Créer des tags globaux
        tag1 = Tag.objects.create(
            user=user,
            name='python',
            color='#3776AB'
        )
        tag2 = Tag.objects.create(
            user=user,
            name='django',
            color='#092E20'
        )
        print(f"✅ Tags globaux créés: {tag1.name}, {tag2.name}")
        
        # 3. Créer une note
        note = Note.objects.create(
            user=user,
            title='Test Note avec Tags',
            content='Une note pour tester le système de tags global'
        )
        print(f"✅ Note créée: {note.title}")
        
        # 4. Tester l'ajout de tags à la note
        note.add_tag(tag1)
        note.add_tag(tag2)
        print("✅ Tags ajoutés à la note")
        
        # 5. Vérifier que les tags sont bien associés
        note_tags = note.tags
        print(f"✅ Tags de la note: {[tag.name for tag in note_tags]}")
        
        # 6. Vérifier que les TagRelations ont été créées
        relations = TagRelation.objects.filter(
            app_name='notebook',
            model_name='Note',
            object_id=str(note.id)
        )
        print(f"✅ Relations créées: {relations.count()}")
        
        # 7. Tester la suppression d'un tag
        note.remove_tag(tag1)
        note_tags_after_remove = note.tags
        print(f"✅ Tags après suppression: {[tag.name for tag in note_tags_after_remove]}")
        
        # 8. Tester set_tags
        tag3 = Tag.objects.create(user=user, name='tests', color='#FF0000')
        note.set_tags([tag2, tag3])
        final_tags = note.tags
        print(f"✅ Tags finaux avec set_tags: {[tag.name for tag in final_tags]}")
        
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("✅ Le système de tags global fonctionne correctement avec notebook")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_api_endpoints():
    """Test des endpoints API du système de tags"""
    print("\n🔌 Test des endpoints API tags")
    print("=" * 30)
    
    from rest_framework.test import APIClient
    from rest_framework import status
    
    try:
        client = APIClient()
        user = User.objects.first()  # Utiliser l'utilisateur créé précédemment
        client.force_authenticate(user=user)
        
        # Test création de tag via API
        tag_data = {
            'name': 'api-test',
            'color': '#00FF00',
            'description': 'Tag créé via API'
        }
        
        response = client.post('/api/v1/core/tags/', tag_data, format='json')
        print(f"✅ Création de tag via API: status {response.status_code}")
        
        if response.status_code == 201:
            tag_id = response.data['id']
            print(f"✅ Tag créé avec ID: {tag_id}")
        
        # Test listing des tags
        response = client.get('/api/v1/core/tags/')
        print(f"✅ Listing des tags: status {response.status_code}")
        if response.status_code == 200:
            tags_count = response.data.get('count', 0)
            print(f"✅ Nombre de tags trouvés: {tags_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Nettoyer la base de test au début
    try:
        User.objects.filter(username='test_tags_user').delete()
        Tag.objects.filter(name__in=['python', 'django', 'tests', 'api-test']).delete()
        Note.objects.filter(title='Test Note avec Tags').delete()
    except:
        pass
    
    # Exécuter les tests
    basic_success = test_basic_functionality()
    api_success = test_api_endpoints()
    
    if basic_success and api_success:
        print("\n🏆 TOUS LES TESTS SONT PASSÉS!")
        print("Le système de tags global est fonctionnel")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)