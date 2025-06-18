"""
Script de test pour vérifier que les endpoints de settings fonctionnent
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
SESSION = requests.Session()

def test_login():
    """Test de connexion"""
    print("1. Test de connexion...")
    response = SESSION.post(f"{BASE_URL}/login/", data={
        'username': 'testuser',  # Remplacez par vos identifiants
        'password': 'testpass'
    })
    if response.status_code == 200:
        print("✅ Connexion réussie")
        return True
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        return False

def test_profile_update():
    """Test de mise à jour du profil"""
    print("\n2. Test de mise à jour du profil...")
    
    # Get CSRF token
    response = SESSION.get(f"{BASE_URL}/settings/")
    if 'csrftoken' in SESSION.cookies:
        csrf_token = SESSION.cookies['csrftoken']
    else:
        print("❌ Pas de CSRF token trouvé")
        return False
    
    # Update profile
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    data = {
        'first_name': 'Test',
        'last_name': 'User',
        'bio': 'Test bio'
    }
    
    response = SESSION.patch(
        f"{BASE_URL}/api/auth/settings/",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print("✅ Profil mis à jour avec succès")
        print(f"   Réponse: {response.json()}")
        return True
    else:
        print(f"❌ Échec de mise à jour: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False

def test_settings_stats():
    """Test des statistiques"""
    print("\n3. Test des statistiques...")
    response = SESSION.get(f"{BASE_URL}/api/auth/settings/stats/")
    
    if response.status_code == 200:
        print("✅ Statistiques récupérées")
        print(f"   Données: {response.json()}")
        return True
    else:
        print(f"❌ Échec: {response.status_code}")
        return False

def test_export_data():
    """Test d'export des données"""
    print("\n4. Test d'export des données...")
    response = SESSION.get(f"{BASE_URL}/api/auth/export-data/")
    
    if response.status_code == 200:
        print("✅ Export réussi")
        # Vérifier que c'est bien un fichier JSON
        try:
            data = response.json()
            print(f"   Export contient {len(data)} sections")
            return True
        except:
            print("❌ La réponse n'est pas du JSON valide")
            return False
    else:
        print(f"❌ Échec: {response.status_code}")
        return False

if __name__ == "__main__":
    print("=== Test des endpoints de settings ===\n")
    
    # Tester la connexion d'abord
    if test_login():
        # Tester les autres endpoints
        test_profile_update()
        test_settings_stats()
        test_export_data()
    else:
        print("\n⚠️  Impossible de tester sans connexion")
        print("   Assurez-vous que le serveur est lancé et que les identifiants sont corrects")