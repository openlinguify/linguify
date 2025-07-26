#!/usr/bin/env python3

import os
import django
from django.http import HttpRequest
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.views_web import CourseDashboardView

User = get_user_model()

def debug_dashboard_context():
    """Debug du contexte de la vue CourseDashboardView"""
    print("🔍 Debug de la vue CourseDashboardView")
    print("=" * 50)
    
    # Créer une requête factice
    request = HttpRequest()
    request.method = 'GET'
    request.user = User.objects.first()
    
    if not request.user:
        print("❌ Aucun utilisateur trouvé")
        return
    
    print(f"👤 Utilisateur: {request.user.username}")
    
    # Créer la vue et obtenir le contexte
    view = CourseDashboardView()
    view.request = request
    
    try:
        context = view.get_context_data()
        
        print("\n📊 Clés du contexte:")
        for key in context.keys():
            print(f"  - {key}")
        
        print("\n📈 Statistiques utilisateur:")
        user_stats = context.get('user_stats', {})
        for key, value in user_stats.items():
            print(f"  - {key}: {value}")
        
        print("\n🎓 Marketplace Stats:")
        marketplace_stats = context.get('marketplace_stats', {})
        for key, value in marketplace_stats.items():
            print(f"  - {key}: {value}")
        
        print("\n📚 Marketplace Courses:")
        marketplace_courses = context.get('marketplace_courses', [])
        print(f"  - Nombre de groupes de niveau: {len(marketplace_courses)}")
        
        for level_group in marketplace_courses:
            level = level_group.get('level', 'Unknown')
            courses_count = len(level_group.get('courses', []))
            print(f"  - Niveau {level}: {courses_count} cours")
            
            for course in level_group.get('courses', [])[:2]:  # Montrer les 2 premiers
                title = course.get('title', 'Sans titre')
                instructor = course.get('instructor', 'Inconnu')
                price = course.get('price', 0)
                is_free = course.get('is_free', False)
                price_str = 'GRATUIT' if is_free else f'{price}€'
                print(f"    * {title} - {instructor} ({price_str})")
        
        print("\n📖 My Courses:")
        my_courses = context.get('my_courses', [])
        print(f"  - Nombre de mes cours: {len(my_courses)}")
        
        print("\n🔄 Continue Learning:")
        continue_learning = context.get('continue_learning', [])
        print(f"  - Cours à continuer: {len(continue_learning)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du contexte: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_dashboard_context()
    if success:
        print("\n✅ Debug terminé avec succès")
    else:
        print("\n❌ Debug échoué")