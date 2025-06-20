#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status rapide des bases de données (version simple)
"""

import os
import sys
import subprocess

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


def quick_count(env_mode):
    """Compte rapide des éléments principaux"""
    env = os.environ.copy()
    env['DJANGO_ENV'] = env_mode
    
    # Déterminer le répertoire backend
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        result = subprocess.run([
            sys.executable, '-c', '''
import django; django.setup()
from app_manager.models import App
from course.models import Lesson, TheoryContent
from apps.authentication.models import User

print(f"Apps: {App.objects.count()}")
print(f"Lessons: {Lesson.objects.count()}")
print(f"Theory: {TheoryContent.objects.count()}")
print(f"Users: {User.objects.count()}")
'''
        ], env=env, capture_output=True, text=True, timeout=10, cwd=backend_dir)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                'apps': int(lines[0].split(': ')[1]) if len(lines) > 0 else 0,
                'lessons': int(lines[1].split(': ')[1]) if len(lines) > 1 else 0,
                'theory': int(lines[2].split(': ')[1]) if len(lines) > 2 else 0,
                'users': int(lines[3].split(': ')[1]) if len(lines) > 3 else 0
            }
        else:
            return None
    except:
        return None


def main():
    print("⚡ Status rapide")
    print("=" * 30)
    
    # Test développement
    print("🏗️  Développement:", end=" ")
    dev_stats = quick_count('development')
    if dev_stats:
        print("✅ Connecté")
        print(f"   Apps: {dev_stats['apps']} | Lessons: {dev_stats['lessons']} | Theory: {dev_stats['theory']} | Users: {dev_stats['users']}")
    else:
        print("❌ Indisponible")
    
    # Test production
    print("🚀 Production:", end=" ")
    prod_stats = quick_count('production')
    if prod_stats:
        print("✅ Connecté")
        print(f"   Apps: {prod_stats['apps']} | Lessons: {prod_stats['lessons']} | Theory: {prod_stats['theory']} | Users: {prod_stats['users']}")
    else:
        print("❌ Indisponible")
    
    # Comparaison rapide
    if dev_stats and prod_stats:
        print()
        print("📊 Différences:")
        diff_apps = dev_stats['apps'] - prod_stats['apps']
        diff_lessons = dev_stats['lessons'] - prod_stats['lessons']
        diff_theory = dev_stats['theory'] - prod_stats['theory']
        
        if diff_apps > 0:
            print(f"   📱 +{diff_apps} apps en dev")
        if diff_lessons > 0:
            print(f"   📚 +{diff_lessons} lessons en dev")
        if diff_theory > 0:
            print(f"   📖 +{diff_theory} theory en dev")
            
        if diff_apps > 0 or diff_lessons > 0 or diff_theory > 0:
            print("   🎯 Déploiement recommandé!")
        else:
            print("   ✅ Synchronisé")


if __name__ == "__main__":
    main()