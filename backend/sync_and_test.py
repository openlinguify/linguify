#!/usr/bin/env python3

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.services.cms_sync import CMSSyncService
from apps.course.models import Unit
from apps.course.api.viewsets import UnitViewSet, UserProgressViewSet

User = get_user_model()

def sync_cms_courses():
    """Synchroniser les cours du CMS"""
    print("🔄 Synchronisation des cours du CMS...")
    
    service = CMSSyncService()
    result = service.sync_published_courses()
    
    print(f"📊 Résultats:")
    print(f"   - Cours traités: {result['total_processed']}")
    print(f"   - Nouveaux cours: {result['created']}")
    print(f"   - Cours mis à jour: {result['updated']}")
    print(f"   - Erreurs: {len(result['errors'])}")
    
    if result['errors']:
        for error in result['errors']:
            print(f"     ❌ {error}")
    
    return result['total_processed'] > 0

def test_units_endpoint():
    """Test l'endpoint units"""
    print("\n🧪 Test de l'endpoint /api/v1/course/units/...")
    
    try:
        # Vérifier s'il y a des units
        units_count = Unit.objects.count()
        print(f"   📚 Nombre d'units dans la base: {units_count}")
        
        if units_count == 0:
            print("   ⚠️  Aucune unit trouvée")
            return False
        
        # Créer un utilisateur test si nécessaire
        user = User.objects.first()
        if not user:
            print("   ⚠️  Aucun utilisateur trouvé")
            return False
        
        print(f"   👤 Utilisateur test: {user.username}")
        
        # Tester l'endpoint
        factory = RequestFactory()
        request = factory.get('/api/v1/course/units/')
        request.user = user
        
        viewset = UnitViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        viewset.action = 'list'
        
        # Test de la liste des units
        response = viewset.list(request)
        print(f"   ✅ Endpoint units - Status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"   📊 Nombre d'units retournées: {len(response.data)}")
            if response.data:
                first_unit = response.data[0]
                print(f"   📝 Premier unit: {first_unit.get('title_en', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_progress_endpoints():
    """Test les endpoints de progression"""
    print("\n🧪 Test des endpoints de progression...")
    
    try:
        user = User.objects.first()
        if not user:
            print("   ⚠️  Aucun utilisateur trouvé")
            return False
        
        factory = RequestFactory()
        request = factory.get('/api/v1/course/progress/dashboard/')
        request.user = user
        
        viewset = UserProgressViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        
        # Test dashboard
        response = viewset.dashboard(request)
        print(f"   ✅ Dashboard endpoint - Status: {response.status_code}")
        
        # Test statistics
        response = viewset.statistics(request)
        print(f"   ✅ Statistics endpoint - Status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Script de synchronisation et test des endpoints")
    print("=" * 50)
    
    # 1. Synchroniser les cours du CMS
    sync_success = sync_cms_courses()
    
    if not sync_success:
        print("❌ Échec de la synchronisation CMS")
        return False
    
    # 2. Tester l'endpoint units
    units_success = test_units_endpoint()
    
    # 3. Tester les endpoints de progression
    progress_success = test_progress_endpoints()
    
    print("\n" + "=" * 50)
    if units_success and progress_success:
        print("🎉 Tous les tests ont réussi!")
        print("🌐 Vous pouvez maintenant tester la page: http://127.0.0.1:8000/learning/?tab=my-learning")
        return True
    else:
        print("❌ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)