#!/usr/bin/env python3
"""
Script interactif pour remplir le vocabulaire par leçons
Permet d'ajouter facilement du vocabulaire à une leçon spécifique
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Use SQLite for testing
os.environ['EMAIL_DEBUG'] = 'True'
os.environ['TEST_MODE'] = 'True'

django.setup()

from apps.course.models import Unit, Lesson, ContentLesson, VocabularyList
from django.db import transaction

class VocabularyFiller:
    def __init__(self):
        self.current_lesson = None
        self.current_content_lesson = None
        
    def list_units(self):
        """Affiche la liste des unités disponibles"""
        print("\n=== UNITÉS DISPONIBLES ===")
        units = Unit.objects.all().order_by('level', 'order')
        for i, unit in enumerate(units, 1):
            print(f"{i}. {unit.title_en} ({unit.level}) - {unit.description_en[:50]}...")
        return units
        
    def list_lessons(self, unit):
        """Affiche les leçons d'une unité"""
        print(f"\n=== LEÇONS DE L'UNITÉ: {unit.title_en} ===")
        lessons = unit.lessons.all().order_by('order')
        for i, lesson in enumerate(lessons, 1):
            vocab_count = VocabularyList.objects.filter(content_lesson__lesson=lesson).count()
            print(f"{i}. {lesson.title_en} ({lesson.lesson_type}) - {vocab_count} mots actuellement")
        return lessons
        
    def list_content_lessons(self, lesson):
        """Affiche les leçons de contenu d'une leçon"""
        print(f"\n=== LEÇONS DE CONTENU POUR: {lesson.title_en} ===")
        content_lessons = lesson.content_lessons.all().order_by('order')
        for i, content_lesson in enumerate(content_lessons, 1):
            vocab_count = content_lesson.vocabulary_lists.count()
            print(f"{i}. {content_lesson.title_en} ({content_lesson.content_type}) - {vocab_count} mots")
        return content_lessons
        
    def show_existing_vocabulary(self, content_lesson):
        """Affiche le vocabulaire existant"""
        vocab_items = content_lesson.vocabulary_lists.all()
        if vocab_items:
            print(f"\n=== VOCABULAIRE EXISTANT ({vocab_items.count()} mots) ===")
            for vocab in vocab_items:
                print(f"• {vocab.word_en} / {vocab.word_fr} / {vocab.word_es} / {vocab.word_nl}")
        else:
            print("\n=== AUCUN VOCABULAIRE EXISTANT ===")
            
    def add_vocabulary_word(self, content_lesson):
        """Ajoute un mot de vocabulaire"""
        print(f"\n=== AJOUTER UN MOT À: {content_lesson.title_en} ===")
        
        # Collecte des informations
        print("Entrez les traductions (appuyez sur Entrée pour passer) :")
        word_en = input("Mot en anglais: ").strip()
        if not word_en:
            print("❌ Le mot en anglais est obligatoire")
            return False
            
        word_fr = input("Mot en français: ").strip() or word_en
        word_es = input("Mot en espagnol: ").strip() or word_en
        word_nl = input("Mot en néerlandais: ").strip() or word_en
        
        print("\nEntrez les définitions :")
        definition_en = input("Définition en anglais: ").strip() or f"Definition of {word_en}"
        definition_fr = input("Définition en français: ").strip() or f"Définition de {word_fr}"
        definition_es = input("Définition en espagnol: ").strip() or f"Definición de {word_es}"
        definition_nl = input("Définition en néerlandais: ").strip() or f"Definitie van {word_nl}"
        
        print("\nEntrez les types de mots :")
        word_type_en = input("Type en anglais (ex: noun, verb): ").strip() or "noun"
        word_type_fr = input("Type en français (ex: nom, verbe): ").strip() or "nom"
        word_type_es = input("Type en espagnol (ex: sustantivo, verbo): ").strip() or "sustantivo"
        word_type_nl = input("Type en néerlandais (ex: zelfstandig, werkwoord): ").strip() or "zelfstandig"
        
        # Phrases d'exemple (optionnel)
        print("\nPhrases d'exemple (optionnel) :")
        example_en = input("Exemple en anglais: ").strip()
        example_fr = input("Exemple en français: ").strip()
        example_es = input("Exemple en espagnol: ").strip()
        example_nl = input("Exemple en néerlandais: ").strip()
        
        try:
            with transaction.atomic():
                vocab = VocabularyList.objects.create(
                    content_lesson=content_lesson,
                    word_en=word_en,
                    word_fr=word_fr,
                    word_es=word_es,
                    word_nl=word_nl,
                    definition_en=definition_en,
                    definition_fr=definition_fr,
                    definition_es=definition_es,
                    definition_nl=definition_nl,
                    word_type_en=word_type_en,
                    word_type_fr=word_type_fr,
                    word_type_es=word_type_es,
                    word_type_nl=word_type_nl,
                    example_sentence_en=example_en,
                    example_sentence_fr=example_fr,
                    example_sentence_es=example_es,
                    example_sentence_nl=example_nl,
                )
                print(f"✅ Mot '{word_en}' ajouté avec succès (ID: {vocab.id})")
                return True
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout: {e}")
            return False
            
    def bulk_add_vocabulary(self, content_lesson):
        """Ajoute plusieurs mots en mode batch"""
        print(f"\n=== AJOUT EN LOT POUR: {content_lesson.title_en} ===")
        print("Format: mot_en|mot_fr|mot_es|mot_nl|definition_en")
        print("Exemple: apple|pomme|manzana|appel|A red or green fruit")
        print("Tapez 'DONE' pour terminer\n")
        
        added_count = 0
        while True:
            line = input("Entrée: ").strip()
            if line.upper() == 'DONE':
                break
                
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) < 5:
                print("❌ Format incorrect. Utilisez: mot_en|mot_fr|mot_es|mot_nl|definition_en")
                continue
                
            try:
                with transaction.atomic():
                    vocab = VocabularyList.objects.create(
                        content_lesson=content_lesson,
                        word_en=parts[0].strip(),
                        word_fr=parts[1].strip(),
                        word_es=parts[2].strip(),
                        word_nl=parts[3].strip(),
                        definition_en=parts[4].strip(),
                        definition_fr=parts[4].strip(),  # Use English definition as fallback
                        definition_es=parts[4].strip(),
                        definition_nl=parts[4].strip(),
                        word_type_en="noun",
                        word_type_fr="nom",
                        word_type_es="sustantivo",
                        word_type_nl="zelfstandig"
                    )
                    print(f"✅ '{parts[0].strip()}' ajouté")
                    added_count += 1
            except Exception as e:
                print(f"❌ Erreur pour '{parts[0].strip()}': {e}")
                
        print(f"\n🎉 {added_count} mots ajoutés avec succès!")
        
    def run(self):
        """Lance le script interactif"""
        print("🎯 SCRIPT INTERACTIF POUR REMPLIR LE VOCABULAIRE")
        print("=" * 50)
        
        try:
            # Sélection de l'unité
            units = self.list_units()
            if not units:
                print("❌ Aucune unité trouvée")
                return
                
            unit_choice = input(f"\nChoisissez une unité (1-{len(units)}): ").strip()
            try:
                selected_unit = units[int(unit_choice) - 1]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return
                
            # Sélection de la leçon
            lessons = self.list_lessons(selected_unit)
            if not lessons:
                print("❌ Aucune leçon trouvée pour cette unité")
                return
                
            lesson_choice = input(f"\nChoisissez une leçon (1-{len(lessons)}): ").strip()
            try:
                selected_lesson = lessons[int(lesson_choice) - 1]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return
                
            # Sélection de la leçon de contenu
            content_lessons = self.list_content_lessons(selected_lesson)
            if not content_lessons:
                print("❌ Aucune leçon de contenu trouvée")
                return
                
            content_choice = input(f"\nChoisissez une leçon de contenu (1-{len(content_lessons)}): ").strip()
            try:
                selected_content_lesson = content_lessons[int(content_choice) - 1]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return
                
            self.current_content_lesson = selected_content_lesson
            
            # Affichage du vocabulaire existant
            self.show_existing_vocabulary(selected_content_lesson)
            
            # Menu principal
            while True:
                print(f"\n=== MENU POUR: {selected_content_lesson.title_en} ===")
                print("1. Ajouter un mot individuellement")
                print("2. Ajouter plusieurs mots en lot")
                print("3. Voir le vocabulaire existant")
                print("4. Quitter")
                
                choice = input("\nVotre choix: ").strip()
                
                if choice == '1':
                    self.add_vocabulary_word(selected_content_lesson)
                elif choice == '2':
                    self.bulk_add_vocabulary(selected_content_lesson)
                elif choice == '3':
                    self.show_existing_vocabulary(selected_content_lesson)
                elif choice == '4':
                    print("👋 Au revoir!")
                    break
                else:
                    print("❌ Choix invalide")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Script interrompu par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    filler = VocabularyFiller()
    filler.run()