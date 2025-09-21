#!/usr/bin/env python
"""
Script pour créer des données de cours d'anglais réalistes
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.language_learning.models import (
    Language, CourseUnit, CourseModule,
    UserLearningProfile, UserLanguage
)
from django.contrib.auth import get_user_model

User = get_user_model()

def create_english_course():
    """Crée un cours d'anglais complet avec 2 unités"""

    # 1. Créer ou récupérer la langue anglaise
    english, created = Language.objects.get_or_create(
        code='EN',
        defaults={
            'name': 'English',
            'native_name': 'English',
            'flag_emoji': '🇬🇧',
            'is_active': True
        }
    )

    if created:
        print("✅ Langue anglaise créée")
    else:
        print("✅ Langue anglaise trouvée")

    # 2. Supprimer les anciennes unités pour recommencer
    print("🧹 Nettoyage des anciennes données...")
    CourseUnit.objects.filter(language=english).delete()

    # ========================================================================
    # UNITÉ 1: Basic English - Greetings and Introductions
    # ========================================================================

    unit1 = CourseUnit.objects.create(
        language=english,
        unit_number=1,
        title="Basic English - Greetings and Introductions",
        description="Learn essential greetings, how to introduce yourself, and basic courtesy expressions in English.",
        icon="bi-handshake",
        color="#10b981",  # Green
        is_active=True,
        order=1
    )

    print(f"📚 Unité 1 créée: {unit1.title}")

    # Modules pour l'Unité 1
    unit1_modules = [
        {
            'module_number': 1,
            'title': 'Basic Greetings',
            'module_type': 'vocabulary',
            'description': 'Learn how to say hello, goodbye, and basic greetings',
            'estimated_duration': 15,
            'content': {
                'vocabulary': [
                    {'en': 'Hello', 'fr': 'Bonjour', 'pronunciation': '/həˈloʊ/'},
                    {'en': 'Good morning', 'fr': 'Bonjour (matin)', 'pronunciation': '/ɡʊd ˈmɔrnɪŋ/'},
                    {'en': 'Good afternoon', 'fr': 'Bonjour (après-midi)', 'pronunciation': '/ɡʊd ˌæftərˈnun/'},
                    {'en': 'Good evening', 'fr': 'Bonsoir', 'pronunciation': '/ɡʊd ˈivnɪŋ/'},
                    {'en': 'Goodbye', 'fr': 'Au revoir', 'pronunciation': '/ɡʊdˈbaɪ/'},
                    {'en': 'See you later', 'fr': 'À plus tard', 'pronunciation': '/si ju ˈleɪtər/'},
                ],
                'exercises': [
                    {
                        'type': 'translation',
                        'question': 'How do you say "Bonjour" in English?',
                        'answer': 'Hello',
                        'options': ['Hello', 'Goodbye', 'Thank you', 'Please']
                    },
                    {
                        'type': 'pronunciation',
                        'word': 'Hello',
                        'phonetic': '/həˈloʊ/',
                        'audio_url': 'audio/hello.mp3'
                    }
                ]
            },
            'xp_reward': 15
        },
        {
            'module_number': 2,
            'title': 'Personal Introductions',
            'module_type': 'speaking',
            'description': 'Learn to introduce yourself and ask for names',
            'estimated_duration': 20,
            'content': {
                'phrases': [
                    {'en': 'My name is...', 'fr': 'Je m\'appelle...', 'example': 'My name is John.'},
                    {'en': 'What\'s your name?', 'fr': 'Comment vous appelez-vous ?', 'example': 'What\'s your name, please?'},
                    {'en': 'Nice to meet you', 'fr': 'Enchanté(e)', 'example': 'Nice to meet you, Sarah!'},
                    {'en': 'I am from...', 'fr': 'Je viens de...', 'example': 'I am from France.'},
                    {'en': 'Where are you from?', 'fr': 'D\'où venez-vous ?', 'example': 'Where are you from?'},
                ],
                'dialogues': [
                    {
                        'title': 'First Meeting',
                        'conversation': [
                            {'speaker': 'A', 'text': 'Hello! My name is Emma.'},
                            {'speaker': 'B', 'text': 'Hi Emma! I\'m David. Nice to meet you.'},
                            {'speaker': 'A', 'text': 'Nice to meet you too, David. Where are you from?'},
                            {'speaker': 'B', 'text': 'I\'m from London. What about you?'},
                            {'speaker': 'A', 'text': 'I\'m from Paris, France.'}
                        ]
                    }
                ]
            },
            'xp_reward': 20
        },
        {
            'module_number': 3,
            'title': 'Polite Expressions',
            'module_type': 'vocabulary',
            'description': 'Essential courtesy words and expressions',
            'estimated_duration': 15,
            'content': {
                'vocabulary': [
                    {'en': 'Please', 'fr': 'S\'il vous plaît', 'pronunciation': '/pliz/'},
                    {'en': 'Thank you', 'fr': 'Merci', 'pronunciation': '/θæŋk ju/'},
                    {'en': 'You\'re welcome', 'fr': 'De rien', 'pronunciation': '/jʊr ˈwɛlkəm/'},
                    {'en': 'Excuse me', 'fr': 'Excusez-moi', 'pronunciation': '/ɪkˈskjuz mi/'},
                    {'en': 'I\'m sorry', 'fr': 'Je suis désolé(e)', 'pronunciation': '/aɪm ˈsɔri/'},
                    {'en': 'No problem', 'fr': 'Pas de problème', 'pronunciation': '/noʊ ˈprɑbləm/'},
                ]
            },
            'xp_reward': 15
        },
        {
            'module_number': 4,
            'title': 'Unit 1 Review',
            'module_type': 'review',
            'description': 'Practice and review all vocabulary and phrases from Unit 1',
            'estimated_duration': 25,
            'content': {
                'review_exercises': [
                    {
                        'type': 'matching',
                        'instructions': 'Match the English phrases with their French translations',
                        'pairs': [
                            {'en': 'Good morning', 'fr': 'Bonjour (matin)'},
                            {'en': 'Thank you', 'fr': 'Merci'},
                            {'en': 'My name is', 'fr': 'Je m\'appelle'},
                            {'en': 'Where are you from?', 'fr': 'D\'où venez-vous ?'}
                        ]
                    },
                    {
                        'type': 'dialogue_completion',
                        'dialogue': [
                            {'speaker': 'A', 'text': 'Hello! _____ name is Marie.'},
                            {'speaker': 'B', 'text': 'Hi Marie! I\'m Tom. _____ to meet you.'},
                            {'speaker': 'A', 'text': '_____ to meet you too!'}
                        ],
                        'options': ['My', 'Nice', 'Nice']
                    }
                ]
            },
            'xp_reward': 25
        }
    ]

    for module_data in unit1_modules:
        module = CourseModule.objects.create(
            unit=unit1,
            **module_data
        )
        print(f"  📖 Module {module.module_number}: {module.title}")

    # ========================================================================
    # UNITÉ 2: Numbers, Time, and Daily Activities
    # ========================================================================

    unit2 = CourseUnit.objects.create(
        language=english,
        unit_number=2,
        title="Numbers, Time, and Daily Activities",
        description="Master numbers, telling time, and describing your daily routine in English.",
        icon="bi-clock",
        color="#3b82f6",  # Blue
        is_active=True,
        order=2
    )

    print(f"📚 Unité 2 créée: {unit2.title}")

    # Modules pour l'Unité 2
    unit2_modules = [
        {
            'module_number': 1,
            'title': 'Numbers 0-100',
            'module_type': 'vocabulary',
            'description': 'Learn to count from 0 to 100 in English',
            'estimated_duration': 20,
            'content': {
                'numbers': {
                    'basic': [
                        {'number': 0, 'word': 'zero', 'pronunciation': '/ˈzɪroʊ/'},
                        {'number': 1, 'word': 'one', 'pronunciation': '/wʌn/'},
                        {'number': 2, 'word': 'two', 'pronunciation': '/tu/'},
                        {'number': 3, 'word': 'three', 'pronunciation': '/θri/'},
                        {'number': 4, 'word': 'four', 'pronunciation': '/fɔr/'},
                        {'number': 5, 'word': 'five', 'pronunciation': '/faɪv/'},
                        {'number': 10, 'word': 'ten', 'pronunciation': '/tɛn/'},
                        {'number': 20, 'word': 'twenty', 'pronunciation': '/ˈtwɛnti/'},
                        {'number': 50, 'word': 'fifty', 'pronunciation': '/ˈfɪfti/'},
                        {'number': 100, 'word': 'one hundred', 'pronunciation': '/wʌn ˈhʌndrəd/'}
                    ]
                },
                'exercises': [
                    {
                        'type': 'listening',
                        'instruction': 'Listen and write the number you hear',
                        'audio_url': 'audio/number_fifteen.mp3',
                        'answer': '15'
                    }
                ]
            },
            'xp_reward': 20
        },
        {
            'module_number': 2,
            'title': 'Telling Time',
            'module_type': 'grammar',
            'description': 'Learn to ask and tell time in English',
            'estimated_duration': 25,
            'content': {
                'time_expressions': [
                    {'time': '3:00', 'formal': 'three o\'clock', 'informal': 'three'},
                    {'time': '3:15', 'formal': 'quarter past three', 'informal': 'three fifteen'},
                    {'time': '3:30', 'formal': 'half past three', 'informal': 'three thirty'},
                    {'time': '3:45', 'formal': 'quarter to four', 'informal': 'three forty-five'},
                ],
                'questions': [
                    {'q': 'What time is it?', 'fr': 'Quelle heure est-il ?'},
                    {'q': 'What time do you...?', 'fr': 'À quelle heure tu... ?'},
                    {'q': 'When do you...?', 'fr': 'Quand est-ce que tu... ?'}
                ],
                'grammar_rules': [
                    'Use "o\'clock" only for exact hours (3:00 = three o\'clock)',
                    'For 15 minutes past: "quarter past" (3:15 = quarter past three)',
                    'For 30 minutes past: "half past" (3:30 = half past three)',
                    'For 45 minutes past: "quarter to" next hour (3:45 = quarter to four)'
                ]
            },
            'xp_reward': 25
        },
        {
            'module_number': 3,
            'title': 'Daily Activities',
            'module_type': 'vocabulary',
            'description': 'Vocabulary for describing your daily routine',
            'estimated_duration': 20,
            'content': {
                'activities': [
                    {'en': 'wake up', 'fr': 'se réveiller', 'example': 'I wake up at 7 AM.'},
                    {'en': 'get up', 'fr': 'se lever', 'example': 'I get up at 7:30 AM.'},
                    {'en': 'have breakfast', 'fr': 'prendre le petit-déjeuner', 'example': 'I have breakfast at 8 AM.'},
                    {'en': 'go to work', 'fr': 'aller au travail', 'example': 'I go to work at 9 AM.'},
                    {'en': 'have lunch', 'fr': 'déjeuner', 'example': 'I have lunch at 12:30 PM.'},
                    {'en': 'come home', 'fr': 'rentrer à la maison', 'example': 'I come home at 6 PM.'},
                    {'en': 'have dinner', 'fr': 'dîner', 'example': 'I have dinner at 7 PM.'},
                    {'en': 'go to bed', 'fr': 'aller se coucher', 'example': 'I go to bed at 10 PM.'}
                ],
                'time_expressions': [
                    {'en': 'in the morning', 'fr': 'le matin'},
                    {'en': 'in the afternoon', 'fr': 'l\'après-midi'},
                    {'en': 'in the evening', 'fr': 'le soir'},
                    {'en': 'at night', 'fr': 'la nuit'}
                ]
            },
            'xp_reward': 20
        },
        {
            'module_number': 4,
            'title': 'My Daily Routine',
            'module_type': 'speaking',
            'description': 'Practice describing your daily schedule',
            'estimated_duration': 30,
            'content': {
                'sample_routine': {
                    'title': 'Sarah\'s Daily Routine',
                    'schedule': [
                        {'time': '7:00 AM', 'activity': 'I wake up and get up immediately.'},
                        {'time': '7:30 AM', 'activity': 'I have breakfast with my family.'},
                        {'time': '8:30 AM', 'activity': 'I go to work by bus.'},
                        {'time': '12:30 PM', 'activity': 'I have lunch with my colleagues.'},
                        {'time': '6:00 PM', 'activity': 'I come home and relax.'},
                        {'time': '7:30 PM', 'activity': 'I have dinner and watch TV.'},
                        {'time': '10:00 PM', 'activity': 'I go to bed.'}
                    ]
                },
                'speaking_exercises': [
                    {
                        'type': 'description',
                        'instruction': 'Describe your morning routine using the vocabulary learned',
                        'prompts': [
                            'What time do you wake up?',
                            'What do you have for breakfast?',
                            'How do you go to work/school?'
                        ]
                    }
                ]
            },
            'xp_reward': 30
        },
        {
            'module_number': 5,
            'title': 'Unit 2 Test',
            'module_type': 'review',
            'description': 'Comprehensive test covering numbers, time, and daily activities',
            'estimated_duration': 35,
            'content': {
                'test_sections': [
                    {
                        'section': 'Numbers',
                        'exercises': [
                            {
                                'type': 'number_recognition',
                                'instruction': 'Write the number in words',
                                'questions': [
                                    {'number': 47, 'answer': 'forty-seven'},
                                    {'number': 83, 'answer': 'eighty-three'}
                                ]
                            }
                        ]
                    },
                    {
                        'section': 'Time',
                        'exercises': [
                            {
                                'type': 'time_telling',
                                'instruction': 'Write the time in words',
                                'questions': [
                                    {'time': '2:15', 'answer': 'quarter past two'},
                                    {'time': '5:45', 'answer': 'quarter to six'}
                                ]
                            }
                        ]
                    },
                    {
                        'section': 'Daily Activities',
                        'exercises': [
                            {
                                'type': 'routine_description',
                                'instruction': 'Complete the daily routine',
                                'text': 'I _____ at 7 AM, then I _____ breakfast at 8 AM.',
                                'answers': ['wake up', 'have']
                            }
                        ]
                    }
                ]
            },
            'xp_reward': 35
        }
    ]

    for module_data in unit2_modules:
        module = CourseModule.objects.create(
            unit=unit2,
            **module_data
        )
        print(f"  📖 Module {module.module_number}: {module.title}")

    print(f"\n🎉 Cours d'anglais créé avec succès !")
    print(f"📊 Statistiques:")
    print(f"   • 2 unités créées")
    print(f"   • {CourseModule.objects.filter(unit__language=english).count()} modules au total")
    print(f"   • Durée totale estimée: {sum(m.estimated_duration for m in CourseModule.objects.filter(unit__language=english))} minutes")

    return english


def setup_user_for_english(username='lplalou3@gmail.com'):
    """Configure un utilisateur pour apprendre l'anglais"""
    try:
        user = User.objects.get(email=username)

        # Mettre à jour le profil d'apprentissage
        profile, created = UserLearningProfile.objects.get_or_create(user=user)
        profile.native_language = 'FR'
        profile.target_language = 'EN'
        profile.language_level = 'A1'
        profile.objectives = 'Study'
        profile.save()

        # Créer ou mettre à jour UserLanguage pour l'anglais
        english = Language.objects.get(code='EN')
        user_language, created = UserLanguage.objects.get_or_create(
            user=user,
            language=english,
            defaults={
                'language_level': 'A1',
                'target_level': 'B2',
                'daily_goal': 15,
                'is_active': True
            }
        )

        print(f"✅ Utilisateur {username} configuré pour apprendre l'anglais")
        print(f"   • Niveau actuel: {user_language.language_level}")
        print(f"   • Objectif: {user_language.target_level}")

    except User.DoesNotExist:
        print(f"❌ Utilisateur {username} non trouvé")


if __name__ == '__main__':
    print("🚀 Création du cours d'anglais...")
    english = create_english_course()
    setup_user_for_english()
    print("\n✅ Terminé ! Vous pouvez maintenant tester l'interface.")