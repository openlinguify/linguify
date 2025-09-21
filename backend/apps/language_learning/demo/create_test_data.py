#!/usr/bin/env python3
"""
Script pour créer des données de test pour l'app language_learning
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/mnt/c/Users/louis/WebstormProjects/linguify/backend')
django.setup()

from apps.language_learning.models import *
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    print("🚀 Création des données de test pour Language Learning...")

    # Créer ou récupérer les langues
    languages_data = [
        {'code': 'EN', 'name': 'English', 'native_name': 'English', 'flag_emoji': '🇬🇧'},
        {'code': 'FR', 'name': 'Français', 'native_name': 'Français', 'flag_emoji': '🇫🇷'},
        {'code': 'ES', 'name': 'Español', 'native_name': 'Español', 'flag_emoji': '🇪🇸'},
        {'code': 'NL', 'name': 'Dutch', 'native_name': 'Nederlands', 'flag_emoji': '🇳🇱'},
    ]

    languages = {}
    for lang_data in languages_data:
        language, created = Language.objects.get_or_create(
            code=lang_data['code'],
            defaults={
                'name': lang_data['name'],
                'native_name': lang_data['native_name'],
                'flag_emoji': lang_data['flag_emoji'],
                'is_active': True
            }
        )
        languages[lang_data['code']] = language
        print(f"{'✅ Créé' if created else '📝 Mis à jour'}: {language.name}")

    # Créer des unités de cours pour l'anglais
    english = languages['EN']
    units_data = [
        {
            'unit_number': 1,
            'title': 'Basic Greetings',
            'description': 'Learn how to greet people and introduce yourself',
            'order': 1
        },
        {
            'unit_number': 2,
            'title': 'Numbers and Time',
            'description': 'Master numbers, dates, and telling time',
            'order': 2
        },
        {
            'unit_number': 3,
            'title': 'Family and Relationships',
            'description': 'Vocabulary about family members and relationships',
            'order': 3
        },
        {
            'unit_number': 4,
            'title': 'Food and Restaurants',
            'description': 'Order food, describe meals, and restaurant vocabulary',
            'order': 4
        }
    ]

    units = []
    for unit_data in units_data:
        unit, created = CourseUnit.objects.get_or_create(
            language=english,
            unit_number=unit_data['unit_number'],
            defaults={
                'title': unit_data['title'],
                'description': unit_data['description'],
                'order': unit_data['order'],
                'is_active': True
            }
        )
        units.append(unit)
        print(f"{'✅ Créé' if created else '📝 Mis à jour'}: Unit {unit.unit_number} - {unit.title}")

    # Créer des modules pour chaque unité
    modules_by_unit = {
        1: [  # Basic Greetings
            {'num': 1, 'title': 'Hello and Goodbye', 'type': 'vocabulary', 'duration': 10, 'xp': 50},
            {'num': 2, 'title': 'Introducing Yourself', 'type': 'conversation', 'duration': 15, 'xp': 75},
            {'num': 3, 'title': 'Polite Expressions', 'type': 'grammar', 'duration': 12, 'xp': 60},
            {'num': 4, 'title': 'Practice Dialogue', 'type': 'listening', 'duration': 20, 'xp': 100},
        ],
        2: [  # Numbers and Time
            {'num': 1, 'title': 'Numbers 1-100', 'type': 'vocabulary', 'duration': 15, 'xp': 75},
            {'num': 2, 'title': 'Days and Months', 'type': 'vocabulary', 'duration': 12, 'xp': 60},
            {'num': 3, 'title': 'Telling Time', 'type': 'grammar', 'duration': 18, 'xp': 90},
            {'num': 4, 'title': 'Time Expressions', 'type': 'conversation', 'duration': 15, 'xp': 75},
        ],
        3: [  # Family and Relationships
            {'num': 1, 'title': 'Family Members', 'type': 'vocabulary', 'duration': 10, 'xp': 50},
            {'num': 2, 'title': 'Describing People', 'type': 'grammar', 'duration': 16, 'xp': 80},
            {'num': 3, 'title': 'Family Stories', 'type': 'reading', 'duration': 20, 'xp': 100},
        ],
        4: [  # Food and Restaurants
            {'num': 1, 'title': 'Food Vocabulary', 'type': 'vocabulary', 'duration': 12, 'xp': 60},
            {'num': 2, 'title': 'At the Restaurant', 'type': 'conversation', 'duration': 18, 'xp': 90},
            {'num': 3, 'title': 'Cooking Verbs', 'type': 'grammar', 'duration': 14, 'xp': 70},
            {'num': 4, 'title': 'Food Culture', 'type': 'reading', 'duration': 22, 'xp': 110},
            {'num': 5, 'title': 'Restaurant Review', 'type': 'writing', 'duration': 25, 'xp': 125},
        ]
    }

    for unit in units:
        if unit.unit_number in modules_by_unit:
            for module_data in modules_by_unit[unit.unit_number]:
                module, created = CourseModule.objects.get_or_create(
                    unit=unit,
                    module_number=module_data['num'],
                    defaults={
                        'title': module_data['title'],
                        'description': f"Learn about {module_data['title'].lower()}",
                        'module_type': module_data['type'],
                        'order': module_data['num'],
                        'estimated_duration': module_data['duration'],
                        'xp_reward': module_data['xp'],
                        'is_locked': False
                    }
                )
                print(f"  {'✅ Créé' if created else '📝 Mis à jour'}: Module {module.module_number} - {module.title}")

    # Créer des profils d'apprentissage pour les utilisateurs existants
    users = User.objects.all()[:3]  # Prendre les 3 premiers utilisateurs

    for user in users:
        # Créer un profil d'apprentissage
        profile, created = UserLearningProfile.objects.get_or_create(
            user=user,
            defaults={
                'native_language': 'FR',
                'target_language': 'EN',
                'language_level': 'A2',
                'objectives': 'Améliorer mon anglais professionnel',
                'streak_count': 5,
                'total_time_spent': 120,  # minutes
                'progress_percentage': 25
            }
        )
        print(f"{'✅ Créé' if created else '📝 Mis à jour'}: Profil pour {user.username}")

        # Créer une progression de cours
        progress, created = UserCourseProgress.objects.get_or_create(
            user=user,
            language=english,
            defaults={
                'level': 2,
                'total_xp': 450
            }
        )
        print(f"{'✅ Créé' if created else '📝 Mis à jour'}: Progression cours pour {user.username}")

        # Créer des progressions de module (simuler que l'utilisateur a complété quelques modules)
        completed_modules = [
            (1, 1), (1, 2), (1, 3),  # Unit 1, modules 1-3 complétés
            (2, 1), (2, 2),          # Unit 2, modules 1-2 complétés
        ]

        for unit_num, module_num in completed_modules:
            try:
                unit = CourseUnit.objects.get(language=english, unit_number=unit_num)
                module = CourseModule.objects.get(unit=unit, module_number=module_num)

                mod_progress, created = ModuleProgress.objects.get_or_create(
                    user=user,
                    module=module,
                    defaults={
                        'is_completed': True,
                        'score': 85,
                        'attempts': 1,
                        'time_spent': module.estimated_duration
                    }
                )
                if created:
                    print(f"  ✅ Progression: {user.username} - Unit {unit_num} Module {module_num}")
            except (CourseUnit.DoesNotExist, CourseModule.DoesNotExist):
                continue

    print("\n🎉 Données de test créées avec succès !")
    print(f"📊 Langues: {Language.objects.count()}")
    print(f"📚 Unités: {CourseUnit.objects.count()}")
    print(f"🧩 Modules: {CourseModule.objects.count()}")
    print(f"👥 Profils d'apprentissage: {UserLearningProfile.objects.count()}")
    print(f"📈 Progressions de cours: {UserCourseProgress.objects.count()}")
    print(f"✅ Progressions de modules: {ModuleProgress.objects.count()}")

if __name__ == '__main__':
    create_test_data()