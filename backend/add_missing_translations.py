#!/usr/bin/env python3
"""
Script pour ajouter les traductions manquantes identifiées sur la page
"""

import re

# Nouvelles traductions françaises manquantes
FRENCH_MISSING = {
    'A complete suite of open source educational apps: memorization, flashcards, note-taking, quizzes, collaborative chat and much more.': 'Une suite complète d\'applications éducatives open source : mémorisation, flashcards, prise de notes, quiz, chat collaboratif et bien plus.',
    'Discover our complete suite of educational apps designed to transform your learning experience. Choose one for free or access all with Premium.': 'Découvrez notre suite complète d\'applications éducatives conçues pour transformer votre expérience d\'apprentissage. Choisissez-en une gratuitement ou accédez à toutes avec Premium.',
    'Structured courses with progressive lessons, interactive exercises and personalized assessments.': 'Cours structurés avec leçons progressives, exercices interactifs et évaluations personnalisées.',
    'Spaced repetition system with smart flashcards for optimal memorization.': 'Système de répétition espacée avec flashcards intelligentes pour une mémorisation optimale.',
    'Centralized note-taking with intelligent organization and advanced search.': 'Prise de notes centralisée avec organisation intelligente et recherche avancée.',
    'Adaptive quiz system to test your knowledge and identify weak points.': 'Système de quiz adaptatif pour tester vos connaissances et identifier les points faibles.',
    'Connect with other learners, share progress and discover content created by the community.': 'Connectez-vous avec d\'autres apprenants, partagez vos progrès et découvrez le contenu créé par la communauté.',
    'Real-time collaborative chat for study groups and language exchange with other learners.': 'Chat collaboratif en temps réel pour les groupes d\'étude et l\'échange linguistique avec d\'autres apprenants.',
    'AI assistant for natural conversations and intelligent real-time corrections.': 'Assistant IA pour des conversations naturelles et des corrections intelligentes en temps réel.',
    'Join the Open Source Revolution': 'Rejoignez la Révolution Open Source',
    'Open Linguify is built by the community, for the community. Help us create the future of education by contributing to our open source project.': 'Open Linguify est construit par la communauté, pour la communauté. Aidez-nous à créer l\'avenir de l\'éducation en contribuant à notre projet open source.',
    'Contribute code and new features': 'Contribuer du code et de nouvelles fonctionnalités',
    'Report bugs and suggest improvements': 'Signaler des bugs et suggérer des améliorations',
    'Help with translations and documentation': 'Aider avec les traductions et la documentation',
    'Open Source Stats': 'Statistiques Open Source',
    'Growing community of contributors': 'Communauté croissante de contributeurs',
    'Contributors': 'Contributeurs',
    'Commits': 'Commits',
    'License': 'Licence',
    'Latest Release': 'Dernière Version',
    'Join our community and access a complete suite of open source educational apps.': 'Rejoignez notre communauté et accédez à une suite complète d\'applications éducatives open source.',
    'Open source educational apps platform: memorization, flashcards, notes, quizzes and collaborative chat.': 'Plateforme d\'applications éducatives open source : mémorisation, flashcards, notes, quiz et chat collaboratif.',
    'Contribute': 'Contribuer'
}

# Nouvelles traductions espagnoles manquantes
SPANISH_MISSING = {
    'A complete suite of open source educational apps: memorization, flashcards, note-taking, quizzes, collaborative chat and much more.': 'Una suite completa de aplicaciones educativas open source: memorización, flashcards, toma de notas, cuestionarios, chat colaborativo y mucho más.',
    'Discover our complete suite of educational apps designed to transform your learning experience. Choose one for free or access all with Premium.': 'Descubre nuestra suite completa de aplicaciones educativas diseñadas para transformar tu experiencia de aprendizaje. Elige una gratis o accede a todas con Premium.',
    'Structured courses with progressive lessons, interactive exercises and personalized assessments.': 'Cursos estructurados con lecciones progresivas, ejercicios interactivos y evaluaciones personalizadas.',
    'Spaced repetition system with smart flashcards for optimal memorization.': 'Sistema de repetición espaciada con flashcards inteligentes para una memorización óptima.',
    'Centralized note-taking with intelligent organization and advanced search.': 'Toma de notas centralizada con organización inteligente y búsqueda avanzada.',
    'Adaptive quiz system to test your knowledge and identify weak points.': 'Sistema de cuestionarios adaptativos para evaluar tus conocimientos e identificar puntos débiles.',
    'Connect with other learners, share progress and discover content created by the community.': 'Conecta con otros estudiantes, comparte tu progreso y descubre contenido creado por la comunidad.',
    'Real-time collaborative chat for study groups and language exchange with other learners.': 'Chat colaborativo en tiempo real para grupos de estudio e intercambio de idiomas con otros estudiantes.',
    'AI assistant for natural conversations and intelligent real-time corrections.': 'Asistente de IA para conversaciones naturales y correcciones inteligentes en tiempo real.',
    'Join the Open Source Revolution': 'Únete a la Revolución Open Source',
    'Open Linguify is built by the community, for the community. Help us create the future of education by contributing to our open source project.': 'Open Linguify está construido por la comunidad, para la comunidad. Ayúdanos a crear el futuro de la educación contribuyendo a nuestro proyecto open source.',
    'Contribute code and new features': 'Contribuir código y nuevas funcionalidades',
    'Report bugs and suggest improvements': 'Reportar errores y sugerir mejoras',
    'Help with translations and documentation': 'Ayudar con traducciones y documentación',
    'Open Source Stats': 'Estadísticas Open Source',
    'Growing community of contributors': 'Comunidad creciente de contribuidores',
    'Contributors': 'Contribuidores',
    'Commits': 'Commits',
    'License': 'Licencia',
    'Latest Release': 'Última Versión',
    'Join our community and access a complete suite of open source educational apps.': 'Únete a nuestra comunidad y accede a una suite completa de aplicaciones educativas open source.',
    'Open source educational apps platform: memorization, flashcards, notes, quizzes and collaborative chat.': 'Plataforma de aplicaciones educativas open source: memorización, flashcards, notas, cuestionarios y chat colaborativo.',
    'Contribute': 'Contribuir'
}

# Nouvelles traductions néerlandaises manquantes
DUTCH_MISSING = {
    'A complete suite of open source educational apps: memorization, flashcards, note-taking, quizzes, collaborative chat and much more.': 'Een complete suite van open source educatieve apps: memorisatie, flashcards, notities maken, quizzen, collaboratieve chat en veel meer.',
    'Discover our complete suite of educational apps designed to transform your learning experience. Choose one for free or access all with Premium.': 'Ontdek onze complete suite van educatieve apps ontworpen om je leerervaring te transformeren. Kies er één gratis of krijg toegang tot alle met Premium.',
    'Structured courses with progressive lessons, interactive exercises and personalized assessments.': 'Gestructureerde cursussen met progressieve lessen, interactieve oefeningen en gepersonaliseerde beoordelingen.',
    'Spaced repetition system with smart flashcards for optimal memorization.': 'Herhalingssysteem met slimme flashcards voor optimale memorisatie.',
    'Centralized note-taking with intelligent organization and advanced search.': 'Gecentraliseerde notities met intelligente organisatie en geavanceerd zoeken.',
    'Adaptive quiz system to test your knowledge and identify weak points.': 'Adaptief quizsysteem om je kennis te testen en zwakke punten te identificeren.',
    'Connect with other learners, share progress and discover content created by the community.': 'Verbind met andere leerlingen, deel voortgang en ontdek inhoud gemaakt door de gemeenschap.',
    'Real-time collaborative chat for study groups and language exchange with other learners.': 'Real-time collaboratieve chat voor studiegroepen en taaluitwisseling met andere leerlingen.',
    'AI assistant for natural conversations and intelligent real-time corrections.': 'AI-assistent voor natuurlijke gesprekken en intelligente realtime correcties.',
    'Join the Open Source Revolution': 'Sluit je aan bij de Open Source Revolutie',
    'Open Linguify is built by the community, for the community. Help us create the future of education by contributing to our open source project.': 'Open Linguify is gebouwd door de gemeenschap, voor de gemeenschap. Help ons de toekomst van onderwijs te creëren door bij te dragen aan ons open source project.',
    'Contribute code and new features': 'Draag code en nieuwe functies bij',
    'Report bugs and suggest improvements': 'Rapporteer bugs en stel verbeteringen voor',
    'Help with translations and documentation': 'Help met vertalingen en documentatie',
    'Open Source Stats': 'Open Source Statistieken',
    'Growing community of contributors': 'Groeiende gemeenschap van bijdragers',
    'Contributors': 'Bijdragers',
    'Commits': 'Commits',
    'License': 'Licentie',
    'Latest Release': 'Laatste Release',
    'Join our community and access a complete suite of open source educational apps.': 'Sluit je aan bij onze gemeenschap en krijg toegang tot een complete suite van open source educatieve apps.',
    'Open source educational apps platform: memorization, flashcards, notes, quizzes and collaborative chat.': 'Open source educatieve apps platform: memorisatie, flashcards, notities, quizzen en collaboratieve chat.',
    'Contribute': 'Bijdragen'
}

def add_missing_translation(file_path, english_text, translation):
    """Add a missing translation to a .po file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the new translation at the end of the file
    new_entry = f'\nmsgid "{english_text}"\nmsgstr "{translation}"\n'
    
    # Only add if not already present
    if f'msgid "{english_text}"' not in content:
        content = content.rstrip() + new_entry
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def apply_missing_translations(file_path, translations):
    """Apply all missing translations to a .po file"""
    added_count = 0
    for english, translation in translations.items():
        if add_missing_translation(file_path, english, translation):
            added_count += 1
    return added_count

def main():
    # Apply missing French translations
    fr_added = apply_missing_translations('public_web/i18n/fr/LC_MESSAGES/django.po', FRENCH_MISSING)
    print(f"Added {fr_added} missing French translations")
    
    # Apply missing Spanish translations
    es_added = apply_missing_translations('public_web/i18n/es/LC_MESSAGES/django.po', SPANISH_MISSING)
    print(f"Added {es_added} missing Spanish translations")
    
    # Apply missing Dutch translations
    nl_added = apply_missing_translations('public_web/i18n/nl/LC_MESSAGES/django.po', DUTCH_MISSING)
    print(f"Added {nl_added} missing Dutch translations")
    
    print(f"Total missing translations added: {fr_added + es_added + nl_added}")

if __name__ == "__main__":
    main()