#!/usr/bin/env python3

import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()

def test_learning_page():
    """Test direct de la page d'apprentissage"""
    print("🧪 Test de la page d'apprentissage")
    print("=" * 50)
    
    # Créer un client et se connecter
    client = Client()
    user = User.objects.first()
    
    if not user:
        print("❌ Aucun utilisateur trouvé")
        return False
    
    client.force_login(user)
    print(f"👤 Connecté en tant que: {user.username}")
    
    # Tester la page d'apprentissage
    response = client.get('/learning/')
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Chercher des indices dans le HTML
        print("\n🔍 Analyse du contenu HTML:")
        
        if 'marketplace-courses' in content:
            print("✅ Section marketplace-courses trouvée")
        else:
            print("❌ Section marketplace-courses manquante")
        
        if 'my-learning' in content:
            print("✅ Section my-learning trouvée")
        else:
            print("❌ Section my-learning manquante")
        
        if 'dashboardData' in content:
            print("✅ Script dashboardData trouvé")
        else:
            print("❌ Script dashboardData manquant")
        
        # Chercher les données JSON
        if 'marketplaceCourses' in content:
            print("✅ Données marketplaceCourses trouvées")
        else:
            print("❌ Données marketplaceCourses manquantes")
        
        # Chercher des cours spécifiques
        if 'Français pour Débutants' in content:
            print("✅ Cours 'Français pour Débutants' trouvé")
        else:
            print("❌ Cours 'Français pour Débutants' manquant")
        
        if 'Marie Dupont' in content:
            print("✅ Professeur 'Marie Dupont' trouvé")
        else:
            print("❌ Professeur 'Marie Dupont' manquant")
        
        # Extraire un échantillon du HTML autour des données
        start_pos = content.find('window.dashboardData')
        if start_pos != -1:
            end_pos = content.find('};', start_pos) + 2
            data_section = content[start_pos:end_pos]
            print(f"\n📊 Section dashboardData (tronquée):")
            print(data_section[:300] + "..." if len(data_section) > 300 else data_section)
        
        return True
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_learning_page()
    if success:
        print("\n✅ Test terminé")
    else:
        print("\n❌ Test échoué")