#!/usr/bin/env python3

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.course.api.viewsets import UnitViewSet
from apps.course.models import Unit

User = get_user_model()

def test_units_endpoint():
    """Test l'endpoint units"""
    print("🧪 Test de l'endpoint /api/v1/course/units/...")
    
    try:
        # Vérifier s'il y a des units
        units_count = Unit.objects.count()
        print(f"   📚 Nombre d'units dans la base: {units_count}")
        
        if units_count == 0:
            print("   ⚠️  Aucune unit trouvée")
            return False
        
        # Lister les units
        units = Unit.objects.all()[:3]
        for unit in units:
            print(f"   📖 Unit {unit.id}: {unit.title_en[:30]} (CMS ID: {unit.cms_unit_id})")
        
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
                print(f"   💰 Prix: {first_unit.get('price', 'N/A')}")
                print(f"   🆓 Gratuit: {first_unit.get('is_free', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_units_endpoint()
    print()
    if success:
        print("🎉 Test réussi ! L'endpoint units fonctionne maintenant.")
        print("🌐 Vous pouvez tester la page: http://127.0.0.1:8000/learning/?tab=my-learning")
    else:
        print("❌ Test échoué")