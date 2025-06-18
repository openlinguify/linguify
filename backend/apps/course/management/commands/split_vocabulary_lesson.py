# backend/apps/course/management/commands/split_vocabulary_lesson.py
"""
Commande pour diviser les leçons de vocabulaire trop longues en plusieurs parties.
Usage: python manage.py split_vocabulary_lesson --lesson-id=<id> [options]

Cette commande prend une leçon de vocabulaire existante et la divise en plusieurs 
sous-leçons, en répartissant le vocabulaire entre elles.

Options principales:
  --lesson-id=ID                   ID de la leçon de vocabulaire à diviser
  --parts=N                        Nombre de parties à créer
  --target-unit-id=ID              Placer toutes les nouvelles leçons dans cette unité
  --target-units='11,18,25'        Spécifier différentes unités cibles pour chaque partie
                                   (la partie 2 va à l'unité ID=11, partie 3 à l'unité ID=18, etc.)

Examples:
  # Diviser la leçon 123 en 3 parties (dans la même unité)
  python manage.py split_vocabulary_lesson --lesson-id=123 --parts=3
  
  # Diviser la leçon 123 en 3 parties (partie 1 reste dans l'unité d'origine, 
  # parties 2 et 3 vont dans l'unité 456)
  python manage.py split_vocabulary_lesson --lesson-id=123 --parts=3 --target-unit-id=456
  
  # Diviser la leçon 123 en 3 parties avec distribution dans différentes unités
  # (partie 1 reste dans l'unité d'origine, partie 2 va dans l'unité 456, partie 3 va dans l'unité 789)
  python manage.py split_vocabulary_lesson --lesson-id=123 --parts=3 --target-units='456,789'
"""
from django.core.management.base import BaseCommand
from django.db import transaction, models, connection
from django.db.models import Count
from django.core.exceptions import ValidationError
import math
import random
import logging
import csv
import io
import sys
import re
import json
from apps.course.models import ContentLesson, VocabularyList, Lesson, MatchingExercise, Unit

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Divise les leçons de vocabulaire trop longues en plusieurs sous-leçons'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, required=False, help='ID de la ContentLesson de vocabulaire à diviser')
        parser.add_argument('--min-words', type=int, default=20, help='Nombre minimum de mots pour envisager une division')
        parser.add_argument('--optimal-words', type=int, default=12, help='Nombre optimal de mots par sous-leçon')
        parser.add_argument('--parts', type=int, help='Nombre de parties à créer (si non spécifié, calculé automatiquement)')
        parser.add_argument('--unit-id', type=int, help='Analyser et diviser toutes les leçons de vocabulaire dans cette unité')
        parser.add_argument('--target-unit-id', type=int, help="ID de l'unité où placer TOUTES les nouvelles leçons (Animals 2, etc.). Si non défini, l'unité d'origine est utilisée.")
        parser.add_argument('--target-units', type=str, help="IDs d'unités séparés par des virgules pour assigner SPÉCIFIQUEMENT chaque partie, format: '11,18,25' (la partie 2 va à l'unité 11, partie 3 à l'unité 18, etc.). La partie 1 reste toujours dans l'unité d'origine.")
        parser.add_argument('--export-words', help="Exporter les mots divisés dans un fichier CSV pour validation")
        parser.add_argument('--import-validation', help="Importer un fichier CSV de validation avec la répartition des mots")
        parser.add_argument('--thematic', action='store_true', help='Essayer de regrouper par thème/similarité')
        parser.add_argument('--reorganize', action='store_true', help='Réorganiser les ordres des leçons après division')
        parser.add_argument('--create-matching', action='store_true', help='Créer des exercices de matching pour les nouvelles leçons')
        parser.add_argument('--keep-original', action='store_true', help='Conserver la leçon originale telle quelle')
        parser.add_argument('--interactive', action='store_true', help='Mode interactif pour valider chaque décision')
        parser.add_argument('--manual-selection', action='store_true', help='En mode interactif, permettre la sélection manuelle des mots pour chaque partie')
        parser.add_argument('--word-assignments', type=str, help='Chemin vers un fichier JSON contenant les assignations manuelles des mots')
        parser.add_argument('--dry-run', action='store_true', help='Simuler l\'exécution sans appliquer les changements')
        parser.add_argument('--scan-all', action='store_true', help='Analyser toutes les leçons de vocabulaire')
        parser.add_argument('--auto-optimize', action='store_true', help='Calculer automatiquement le nombre optimal de divisions')

    @transaction.atomic
    def handle(self, *args, **options):
        """Point d'entrée principal de la commande"""
        
        lesson_id = options.get('lesson_id')
        unit_id = options.get('unit_id')
        scan_all = options.get('scan_all')
        min_words = options.get('min_words', 20)
        dry_run = options.get('dry_run', False)
        interactive = options.get('interactive', False)
        
        # Configuration de la transaction
        if dry_run:
            # En mode dry-run, on utilise un savepoint pour annuler toutes les modifications à la fin
            sid = transaction.savepoint()
            self.stdout.write(self.style.WARNING("=== MODE SIMULATION (DRY RUN) ==="))
            self.stdout.write(self.style.WARNING("Aucune modification ne sera appliquée à la base de données"))
            
        # Force la séquence à être mise à jour en fonction de la valeur max actuelle pour éviter les conflits
        with connection.cursor() as cursor:
            cursor.execute("SELECT setval('course_lesson_id_seq', COALESCE((SELECT MAX(id) FROM course_lesson), 1), true);")
            cursor.execute("SELECT setval('course_contentlesson_id_seq', COALESCE((SELECT MAX(id) FROM course_contentlesson), 1), true);")
            cursor.execute("SELECT setval('course_matchingexercise_id_seq', COALESCE((SELECT MAX(id) FROM course_matchingexercise), 1), true);")
        self.stdout.write("Séquences de base de données réinitialisées pour éviter les conflits d'ID.")
            
        try:
            # Déterminer quelles leçons traiter
            if lesson_id:
                # Traiter une seule leçon spécifique
                try:
                    content_lesson = ContentLesson.objects.get(id=lesson_id)
                    self._process_lesson(content_lesson, options)
                except ContentLesson.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Leçon {lesson_id} introuvable"))
                    return
                    
            elif unit_id:
                # Traiter toutes les leçons de vocabulaire d'une unité
                content_lessons = ContentLesson.objects.filter(
                    lesson__unit_id=unit_id, 
                    content_type__icontains='vocabulary'
                ).annotate(word_count=Count('vocabulary_lists'))
                
                if not content_lessons.exists():
                    self.stdout.write(self.style.ERROR(f"Aucune leçon de vocabulaire trouvée dans l'unité {unit_id}"))
                    return
                
                for lesson in content_lessons:
                    if lesson.word_count >= min_words:
                        self._process_lesson(lesson, options)
                    else:
                        self.stdout.write(
                            f"Leçon {lesson.id} ({lesson.title_en}) : {lesson.word_count} mots - ignorée (< {min_words})"
                        )
                        
            elif scan_all:
                # Analyser toutes les leçons de vocabulaire du système
                self.stdout.write("Analyse de toutes les leçons de vocabulaire...")
                
                content_lessons = ContentLesson.objects.filter(
                    content_type__icontains='vocabulary'
                ).annotate(word_count=Count('vocabulary_lists')).order_by('-word_count')
                
                self.stdout.write(self.style.SUCCESS(f"Total de leçons de vocabulaire: {content_lessons.count()}"))
                self.stdout.write("\n=== Leçons de vocabulaire avec le plus de mots ===")
                
                for idx, lesson in enumerate(content_lessons[:10]):
                    self.stdout.write(
                        f"{idx+1}. Leçon {lesson.id} - {lesson.title_en} : {lesson.word_count} mots "
                        f"(Unité: {lesson.lesson.unit.level}-{lesson.lesson.unit.order})"
                    )
                
                to_process = content_lessons.filter(word_count__gte=min_words)
                self.stdout.write(f"\nLeçons éligibles pour division (>= {min_words} mots): {to_process.count()}")
                
                if not dry_run and not options.get('yes', False) and interactive:
                    confirm = input("Voulez-vous traiter toutes ces leçons? [y/N] ")
                    if confirm.lower() != 'y':
                        self.stdout.write("Opération annulée")
                        return
                
                for lesson in to_process:
                    self._process_lesson(lesson, options)
            
            else:
                self.stdout.write(self.style.ERROR("Veuillez spécifier --lesson-id, --unit-id ou --scan-all"))
                return
                
        finally:
            # En mode dry-run, annuler toutes les modifications
            if dry_run:
                transaction.savepoint_rollback(sid)
                self.stdout.write(self.style.WARNING("=== SIMULATION TERMINÉE - Aucune modification appliquée ==="))

    def _process_lesson(self, content_lesson, options):
        """Traite une leçon spécifique pour la diviser si nécessaire"""
        # Check if it's a vocabulary lesson
        if 'vocabulary' not in content_lesson.content_type.lower():
            self.stdout.write(self.style.ERROR(
                f"Leçon {content_lesson.id} ({content_lesson.title_en}) n'est pas une leçon de vocabulaire"
            ))
            return
            
        # Get vocabulary words
        vocabulary = list(VocabularyList.objects.filter(content_lesson=content_lesson))
        count = len(vocabulary)
        
        # Get parent lesson info for better display
        parent_lesson = content_lesson.lesson
        original_lesson_title = parent_lesson.title_en
        current_unit = parent_lesson.unit
        
        self.stdout.write(f"\n=== Traitement de la leçon {content_lesson.id} : {content_lesson.title_en} ===")
        self.stdout.write(f"Leçon parente: {original_lesson_title} (ID: {parent_lesson.id})")
        self.stdout.write(f"Unité actuelle: {current_unit.level}-{current_unit.order} ({current_unit.title_en})")
        self.stdout.write(f"Nombre de mots: {count}")
        
        # Déterminer les unités cibles pour les nouvelles leçons
        target_unit_id = options.get('target_unit_id')
        target_units_str = options.get('target_units')
        default_target_unit = None
        target_units_map = {}
        
        # Cas 1: Unité cible unique pour toutes les parties
        if target_unit_id:
            try:
                default_target_unit = Unit.objects.get(id=target_unit_id)
                self.stdout.write(f"Unité cible par défaut: {default_target_unit.level}-{default_target_unit.order} ({default_target_unit.title_en})")
            except Unit.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Unité cible {target_unit_id} introuvable"))
                if options.get('interactive', False):
                    proceed = input("Continuer avec l'unité actuelle? [y/N] ")
                    if proceed.lower() != 'y':
                        return
                default_target_unit = None
        
        # Cas 2: Unités spécifiques pour chaque partie
        if target_units_str:
            target_unit_ids = target_units_str.split(',')
            for i, unit_id_str in enumerate(target_unit_ids):
                if not unit_id_str.strip():
                    continue
                    
                try:
                    unit_id = int(unit_id_str.strip())
                    part_index = i + 2  # Partie 2, 3, etc.
                    try:
                        unit = Unit.objects.get(id=unit_id)
                        target_units_map[part_index] = unit
                        self.stdout.write(f"Unité cible pour partie {part_index}: {unit.level}-{unit.order} ({unit.title_en})")
                    except Unit.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Unité cible {unit_id} pour partie {part_index} introuvable"))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"ID d'unité invalide: {unit_id_str}"))
        
        # Utiliser l'unité actuelle comme défaut si aucune unité cible n'est spécifiée
        if not default_target_unit:
            default_target_unit = current_unit
            self.stdout.write(f"Unité cible par défaut (même que l'actuelle): {default_target_unit.level}-{default_target_unit.order} ({default_target_unit.title_en})")
        
        # Déterminer le nombre de parties
        optimal_words = options.get('optimal_words', 12)
        parts = options.get('parts')
        
        if not parts and options.get('auto_optimize', False):
            # Calculer le nombre optimal de parties selon différentes métriques
            parts = self._calculate_optimal_parts(count, optimal_words)
        elif not parts:
            # Calculer simplement basé sur le nombre optimal de mots par leçon
            parts = math.ceil(count / optimal_words)
            
        if count < options.get('min_words', 20):
            self.stdout.write(self.style.WARNING(
                f"Cette leçon contient seulement {count} mots, ce qui est inférieur au seuil de {options.get('min_words')}. "
                f"Division non recommandée."
            ))
            if not options.get('force', False) and options.get('interactive', False):
                proceed = input("Procéder quand même? [y/N] ")
                if proceed.lower() != 'y':
                    return
                
        if parts <= 1:
            self.stdout.write(self.style.WARNING(f"Division non nécessaire (parts={parts})"))
            return
            
        self.stdout.write(f"Division en {parts} parties, ~{count // parts} mots par partie")
        
        # Demander une confirmation interactive si nécessaire
        if options.get('interactive', False):
            custom_parts = input(f"Nombre de parties ({parts})? Laissez vide pour confirmer, ou entrez un nouveau nombre: ")
            if custom_parts and custom_parts.isdigit() and int(custom_parts) > 0:
                parts = int(custom_parts)
                self.stdout.write(f"Nouvelle division: {parts} parties, ~{count // parts} mots par partie")
                
        # Vérifier si l'utilisateur souhaite exporter les mots pour validation
        export_file = options.get('export_words')
        if export_file:
            self._export_vocabulary_for_validation(vocabulary, export_file, parts)
            self.stdout.write(self.style.SUCCESS(f"Vocabulaire exporté dans {export_file} pour validation"))
            if not options.get('dry_run', False):
                self.stdout.write("Utilisez --import-validation pour continuer après avoir modifié le fichier")
                return
                
        # Vérifier si l'utilisateur a fourni un fichier de validation
        import_file = options.get('import_validation')
        if import_file:
            try:
                groups = self._import_validation_file(import_file, vocabulary)
                self.stdout.write(self.style.SUCCESS(f"Validation importée: {len(groups)} groupes de mots"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors de l'importation du fichier de validation: {str(e)}"))
                return
        # Vérifier si un fichier d'assignations manuelles est fourni
        elif options.get('word_assignments'):
            word_assignments_file = options.get('word_assignments')
            self.stdout.write(f"Chargement des assignations manuelles depuis: {word_assignments_file}")
            
            try:
                with open(word_assignments_file, 'r') as f:
                    word_assignments = json.load(f)
                
                # Convertir le dictionnaire d'assignations en groupes
                groups = [[] for _ in range(parts)]
                
                # Créer un dictionnaire pour accéder rapidement aux objets vocabulaire par ID
                vocab_dict = {str(word.id): word for word in vocabulary}
                
                # Assigner les mots aux groupes selon les assignations
                for word_id, part_str in word_assignments.items():
                    part = int(part_str)
                    if part < 1 or part > parts:
                        self.stdout.write(self.style.WARNING(f"Partie invalide {part} pour le mot {word_id}, assigné à la partie 1"))
                        part = 1
                    
                    if word_id in vocab_dict:
                        groups[part-1].append(vocab_dict[word_id])
                    
                # Vérifier si tous les mots ont été assignés
                assigned_ids = set(word_assignments.keys())
                all_ids = set(vocab_dict.keys())
                unassigned_ids = all_ids - assigned_ids
                
                if unassigned_ids:
                    self.stdout.write(self.style.WARNING(f"{len(unassigned_ids)} mots non assignés, ils seront ajoutés à la partie 1"))
                    for word_id in unassigned_ids:
                        groups[0].append(vocab_dict[word_id])
                
                self.stdout.write(self.style.SUCCESS(f"Assignation manuelle chargée: {sum(len(g) for g in groups)}/{len(vocabulary)} mots répartis"))
                
                # Afficher la répartition
                for i, group in enumerate(groups):
                    self.stdout.write(f"Partie {i+1}: {len(group)} mots")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors du chargement des assignations manuelles: {str(e)}"))
                self.stdout.write(self.style.WARNING("Utilisation de la répartition automatique comme fallback"))
                
                # Fallback sur la répartition automatique
                items_per_part = count // parts
                random.shuffle(vocabulary)  # Mélanger les mots pour éviter les biais
                
                groups = []
                for i in range(parts):
                    start = i * items_per_part
                    end = start + items_per_part if i < parts-1 else count
                    groups.append(vocabulary[start:end])
        
        # Vérifier si l'utilisateur souhaite faire une sélection manuelle en mode interactif
        elif options.get('interactive', False) and options.get('manual_selection', False):
            # Sélection manuelle des mots pour chaque partie
            groups = self._manually_select_words(vocabulary, parts)
            self.stdout.write(self.style.SUCCESS("Sélection manuelle des mots terminée"))
        else:
            # Plan the division
            if options.get('thematic', False):
                # Groupement thématique - à implémenter pour une future version
                groups = self._group_by_theme(vocabulary, parts)
                self.stdout.write(self.style.SUCCESS("Groupement thématique appliqué"))
            else:
                # Division simple en parties égales
                items_per_part = count // parts
                random.shuffle(vocabulary)  # Mélanger les mots pour éviter les biais
                
                groups = []
                for i in range(parts):
                    start = i * items_per_part
                    end = start + items_per_part if i < parts-1 else count
                    groups.append(vocabulary[start:end])
        
        # Trouver les numéros de leçon existants pour le titre de base
        base_title, current_number = self._parse_lesson_title(original_lesson_title)
        
        # Déterminer l'unité à utiliser pour la recherche des numéros de leçon
        # Si on a une map d'unités cibles, on utilise celle de la partie 2 si disponible, sinon l'unité par défaut
        target_unit_for_numbers = target_units_map.get(2, default_target_unit) if target_units_map else default_target_unit
        
        next_numbers = self._find_next_lesson_numbers(
            base_title, 
            current_number, 
            current_unit, 
            target_unit_for_numbers, 
            parts, 
            target_units_map
        )
        
        first_number = next_numbers[0]
        second_number = next_numbers[1] if len(next_numbers) > 1 else None
        
        # Afficher le plan de division avec les nouveaux numéros
        self._display_division_plan(groups, content_lesson, parent_lesson, current_unit, default_target_unit, 
                                    base_title, first_number, second_number, target_units_map)
        
        # Si mode simulation, on s'arrête ici
        if options.get('dry_run', False):
            return
            
        # Confirmation interactive si demandée
        if options.get('interactive', False):
            confirm = input("Confirmer cette division? [y/N] ")
            if confirm.lower() != 'y':
                self.stdout.write("Division annulée")
                return
            
        # Exécuter la division
        new_lessons = []
        
        # Partie 1: Renommer la leçon existante en "Titre 1" si nécessaire
        if not options.get('keep_original', False):
            # Renommer la leçon originale avec le numéro "1"
            new_title_en = f"{base_title} {first_number}"
            new_title_fr = f"{self._get_base_title(parent_lesson.title_fr)} {first_number}"
            new_title_es = f"{self._get_base_title(parent_lesson.title_es)} {first_number}"
            new_title_nl = f"{self._get_base_title(parent_lesson.title_nl)} {first_number}"
            
            parent_lesson.title_en = new_title_en
            parent_lesson.title_fr = new_title_fr
            parent_lesson.title_es = new_title_es
            parent_lesson.title_nl = new_title_nl
            parent_lesson.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"Renommé la leçon originale en: {parent_lesson.title_en}"
            ))
        
        # Conserver le contenu dans la leçon originale
        first_group = groups[0]
        
        # Create all new content lessons first before reassigning vocabulary words
        new_content_lessons_data = []
        for i in range(1, len(groups)):
            part_number = i + 1
            
            # Determine the lesson number to use
            if i < len(next_numbers):
                lesson_number = next_numbers[i]
            else:
                # If we don't have enough numbers, use a logical sequence
                lesson_number = max(next_numbers) + (i - len(next_numbers) + 1)
                self.stdout.write(self.style.WARNING(
                    f"Pas assez de numéros générés, utilisation du fallback: {lesson_number} pour la partie {part_number}"
                ))
            
            # Determine the target unit for this part
            target_unit_for_part = target_units_map.get(part_number, default_target_unit)
            
            # Check if a lesson with this title already exists in this unit
            existing_title = f"{base_title} {lesson_number}"
            if Lesson.objects.filter(title_en=existing_title, unit=target_unit_for_part).exists():
                self.stdout.write(self.style.WARNING(
                    f"Une leçon intitulée '{existing_title}' existe déjà dans l'unité {target_unit_for_part.title_en}. "
                    f"Ajout d'un suffixe pour éviter les doublons."
                ))
                lesson_number = f"{lesson_number} bis"
            
            # Find the highest order in the target unit and increment by 1 for the new lesson
            max_order = Lesson.objects.filter(unit=target_unit_for_part).aggregate(
                max_order=models.Max('order'))['max_order'] or 0
            new_order = max_order + 1
            
            self.stdout.write(f"Creating new lesson in unit {target_unit_for_part.id} with order {new_order}")
            
            # Log des informations de débogage avant création
            self.stdout.write(f"DEBUG: Création d'une leçon avec les paramètres suivants:")
            self.stdout.write(f"DEBUG: - Unit: {target_unit_for_part.id} ({target_unit_for_part.title_en})")
            self.stdout.write(f"DEBUG: - Lesson type: {parent_lesson.lesson_type}")
            self.stdout.write(f"DEBUG: - Title: {base_title} {lesson_number}")
            self.stdout.write(f"DEBUG: - Order: {new_order}")
            
            try:
                # Create a new lesson in the target unit with a unique order
                # WITHOUT specifying the ID to let the database generate it
                new_lesson = Lesson.objects.create(
                    unit=target_unit_for_part,
                    lesson_type=parent_lesson.lesson_type,
                    professional_field=parent_lesson.professional_field,
                    title_en=f"{base_title} {lesson_number}",
                    title_fr=f"{self._get_base_title(parent_lesson.title_fr)} {lesson_number}",
                    title_es=f"{self._get_base_title(parent_lesson.title_es)} {lesson_number}",
                    title_nl=f"{self._get_base_title(parent_lesson.title_nl)} {lesson_number}",
                    description_en=parent_lesson.description_en,
                    description_fr=parent_lesson.description_fr,
                    description_es=parent_lesson.description_es,
                    description_nl=parent_lesson.description_nl,
                    estimated_duration=parent_lesson.estimated_duration,
                    order=new_order
                )
                self.stdout.write(f"DEBUG: Leçon créée avec succès, ID={new_lesson.id}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERREUR lors de la création de la leçon: {str(e)}"))
                # Récupération de la dernière valeur de séquence
                with connection.cursor() as cursor:
                    cursor.execute("SELECT last_value FROM course_lesson_id_seq;")
                    last_seq = cursor.fetchone()[0]
                    self.stdout.write(f"DEBUG: Dernière valeur de séquence course_lesson_id_seq = {last_seq}")
                    cursor.execute("SELECT MAX(id) FROM course_lesson;")
                    max_id = cursor.fetchone()[0]
                    self.stdout.write(f"DEBUG: Max ID dans course_lesson = {max_id}")
                raise
            
            # Création de ContentLesson avec gestion d'erreurs et débogage
            try:
                # Create a new ContentLesson for this new lesson
                # WITHOUT specifying the ID to let the database generate it automatically
                new_content_lesson = ContentLesson.objects.create(
                    lesson=new_lesson,
                    content_type=content_lesson.content_type,
                    title_en=content_lesson.title_en,
                    title_fr=content_lesson.title_fr,
                    title_es=content_lesson.title_es,
                    title_nl=content_lesson.title_nl,
                    instruction_en=content_lesson.instruction_en,
                    instruction_fr=content_lesson.instruction_fr,
                    instruction_es=content_lesson.instruction_es,
                    instruction_nl=content_lesson.instruction_nl,
                    estimated_duration=content_lesson.estimated_duration,
                    order=content_lesson.order
                )
                self.stdout.write(f"DEBUG: ContentLesson créé avec succès, ID={new_content_lesson.id}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERREUR lors de la création du ContentLesson: {str(e)}"))
                # Récupération de la dernière valeur de séquence
                with connection.cursor() as cursor:
                    cursor.execute("SELECT last_value FROM course_contentlesson_id_seq;")
                    last_seq = cursor.fetchone()[0]
                    self.stdout.write(f"DEBUG: Dernière valeur de séquence course_contentlesson_id_seq = {last_seq}")
                    cursor.execute("SELECT MAX(id) FROM course_contentlesson;")
                    max_id = cursor.fetchone()[0]
                    self.stdout.write(f"DEBUG: Max ID dans course_contentlesson = {max_id}")
                raise
            
            new_content_lessons_data.append((new_content_lesson, groups[i], new_lesson, target_unit_for_part))
        
        # Move words directly to their appropriate content lessons without setting NULL temporarily
        # First, move all words from the first group to the original content lesson
        for word in first_group:
            if word.content_lesson_id != content_lesson.id:
                word.content_lesson = content_lesson
                word.save()
        
        # Then move words for parts 2+ to their new content lessons
        for i, (new_content_lesson, group, new_lesson, target_unit_for_part) in enumerate(new_content_lessons_data):
            part_number = i + 2  # Part 2, 3, etc.
            
            for word in group:
                word.content_lesson = new_content_lesson
                word.save()
                
            self.stdout.write(self.style.SUCCESS(
                f"Créé la partie {part_number}/{len(groups)} avec {len(group)} mots: "
                f"{new_lesson.title_en} dans l'unité {target_unit_for_part.level}-{target_unit_for_part.order} ({target_unit_for_part.title_en})"
            ))
            
            # Create matching exercises if requested
            if options.get('create_matching', False):
                self._create_matching_exercise(new_content_lesson, group)
                
        # Extract just the content lessons for return value
        new_lessons = [cl for cl, _, _, _ in new_content_lessons_data]
            
        self.stdout.write(self.style.SUCCESS(
            f"Conservé {len(first_group)} mots dans la leçon originale: {content_lesson.title_en}"
        ))
        
        # Réorganiser les ordres si demandé
        if options.get('reorganize', False):
            for new_lesson in new_lessons:
                self._reorganize_lesson_order(new_lesson.lesson, [new_lesson])
            
        return new_lessons

    def _parse_lesson_title(self, title):
        """Analyse le titre de la leçon pour séparer le nom de base et le numéro éventuel"""
        # Chercher un numéro à la fin du titre (ex: "Animals 1")
        match = re.search(r'^(.*?)\s+(\d+)$', title)
        if match:
            base_title = match.group(1).strip()
            number = int(match.group(2))
            return base_title, number
        else:
            # Pas de numéro trouvé
            return title, None

    def _get_base_title(self, title):
        """Extrait le titre de base sans numéro"""
        base_title, _ = self._parse_lesson_title(title)
        return base_title

    def _find_next_lesson_numbers(self, base_title, current_number, current_unit, target_unit, parts, target_units_map=None):
        """Trouve les prochains numéros disponibles pour les leçons"""
        # Si on a plusieurs unités cibles, on doit vérifier les numéros existants dans toutes ces unités
        relevant_unit_ids = set()
        relevant_unit_ids.add(current_unit.id)
        relevant_unit_ids.add(target_unit.id if target_unit else current_unit.id)
        
        # Ajouter toutes les autres unités cibles à considérer
        if target_units_map:
            for unit in target_units_map.values():
                relevant_unit_ids.add(unit.id)
        
        # Rechercher toutes les leçons existantes avec le même titre de base dans les unités pertinentes
        existing_lessons = Lesson.objects.filter(
            title_en__regex=r'^{}(\s+\d+)?$'.format(re.escape(base_title)),
            unit_id__in=relevant_unit_ids
        )
        
        self.stdout.write(f"Recherche de numéros existants pour '{base_title}' dans {len(relevant_unit_ids)} unités")
        
        # Collecter tous les numéros existants
        existing_numbers = set()
        for lesson in existing_lessons:
            _, number = self._parse_lesson_title(lesson.title_en)
            if number:
                existing_numbers.add(number)
                self.stdout.write(f"  - Numéro existant trouvé: {number} (Unité: {lesson.unit.title_en})")
                
        self.stdout.write(f"Total de numéros existants trouvés: {len(existing_numbers)}")
        
        # Logique pour déterminer les numéros
        next_numbers = []
        
        # Cas 1: La leçon actuelle n'a pas de numéro (première division)
        if current_number is None:
            # La première partie devient 1
            next_numbers.append(1)
            
            # Les autres parties sont les prochains nombres disponibles
            number = 2
            while len(next_numbers) < parts:
                if number not in existing_numbers:
                    next_numbers.append(number)
                number += 1
        
        # Cas 2: La leçon a déjà un numéro (division d'une leçon déjà divisée)
        else:
            # Garder le même numéro pour la première partie
            next_numbers.append(current_number)
            
            # Les autres parties sont les prochains nombres disponibles
            number = 1
            while len(next_numbers) < parts:
                if number not in existing_numbers and number != current_number:
                    next_numbers.append(number)
                number += 1
                
        # Trier les numéros pour s'assurer que la séquence est logique
        next_numbers.sort()
        
        self.stdout.write(f"Numéros attribués: {next_numbers}")
        return next_numbers

    def _calculate_optimal_parts(self, word_count, optimal_words=12):
        """Calcule le nombre optimal de parties pour une division intelligente"""
        # Base: simple division par le nombre optimal de mots
        base_parts = math.ceil(word_count / optimal_words)
        
        # Heuristiques pour ajuster le nombre de parties
        if word_count <= 24:
            # Pour les petites leçons, 2 parties maximum
            return min(2, base_parts)
        elif word_count <= 36:
            # Pour les leçons moyennes, 3 parties maximum
            return min(3, base_parts)
        elif word_count <= 60:
            # Pour les leçons assez grandes
            # Essayer de faire des groupes de taille similaire
            for parts in range(3, 6):
                if word_count % parts <= parts:
                    return parts
            return min(5, base_parts)
        elif word_count <= 120:
            # Pour les grandes leçons, entre 6 et 10 parties
            # On évite d'avoir trop de leçons avec peu de mots
            min_words_per_lesson = 8
            max_parts = word_count // min_words_per_lesson
            return min(max_parts, 10)
        else:
            # Pour les très grandes leçons, limiter à 12 parties maximum
            # et garantir un minimum de 8 mots par leçon
            min_words_per_lesson = 8
            max_parts = word_count // min_words_per_lesson
            return min(max_parts, 12)

    def _display_division_plan(self, groups, content_lesson, parent_lesson, current_unit, default_target_unit, 
                              base_title, first_number, second_number=None, target_units_map=None):
        """Affiche un résumé du plan de division amélioré"""
        original_title = parent_lesson.title_en
        
        # Préparer les titres pour l'affichage
        first_title = f"{base_title} {first_number}" if first_number is not None else base_title
        second_title = f"{base_title} {second_number}" if second_number is not None else f"{base_title} 2"
        
        self.stdout.write("\n=== PLAN DE DIVISION DÉTAILLÉ ===")
        
        # Afficher si des unités cibles spécifiques sont définies
        if target_units_map:
            self.stdout.write("\nUNITÉS CIBLES SPÉCIFIQUES DÉFINIES:")
            for part_number, target_unit in sorted(target_units_map.items()):
                self.stdout.write(f"  Partie {part_number} → Unité {target_unit.order} ({target_unit.level}): {target_unit.title_en}")
        elif default_target_unit and default_target_unit.id != current_unit.id:
            self.stdout.write(f"\nUNITÉ CIBLE POUR TOUTES LES NOUVELLES PARTIES: {default_target_unit.level}-{default_target_unit.order} ({default_target_unit.title_en})")
        
        # Structure actuelle
        self.stdout.write("\nSTRUCTURE ACTUELLE:")
        self.stdout.write(f"Unit {current_unit.order} ({current_unit.level}): {current_unit.title_en}")
        self.stdout.write(f"  └── Lesson \"{original_title}\" (ID={parent_lesson.id})")
        self.stdout.write(f"      └── ContentLesson \"{content_lesson.title_en}\" (ID={content_lesson.id}) - {len(groups[0]) + sum(len(g) for g in groups[1:])} mots de vocabulaire")
        
        # Structure après division
        self.stdout.write("\nSTRUCTURE APRÈS DIVISION:")
        
        # Première partie - reste dans l'unité actuelle
        self.stdout.write(f"Unit {current_unit.order} ({current_unit.level}): {current_unit.title_en}")
        self.stdout.write(f"  └── Lesson \"{first_title}\" (renommée, ID={parent_lesson.id})")
        self.stdout.write(f"      └── ContentLesson \"{content_lesson.title_en}\" (ID={content_lesson.id}) - {len(groups[0])} mots")
        
        # Afficher quelques exemples du premier groupe
        sample_size = min(3, len(groups[0]))
        samples = random.sample(groups[0], sample_size) if len(groups[0]) >= sample_size else groups[0]
        
        for word in samples:
            self.stdout.write(f"          ├── {word.word_en}: {word.definition_en[:40]}...")
            
        if len(groups[0]) > sample_size:
            self.stdout.write(f"          └── ...et {len(groups[0]) - sample_size} autres mots")
        
        # Partie 2+ - dans les unités cibles
        for i in range(1, len(groups)):
            part_number = i + 1
            group = groups[i]
            
            # Déterminer l'unité cible pour cette partie
            target_unit = target_units_map.get(part_number, default_target_unit) if target_units_map else default_target_unit
            
            # Afficher l'unité seulement si elle est différente de la précédente
            if i == 1 or target_units_map and part_number in target_units_map:
                self.stdout.write(f"\nUnit {target_unit.order} ({target_unit.level}): {target_unit.title_en}")
            
            # Titre avec numéro pour cette partie
            if i == 1 and second_number is not None:
                display_title = second_title
            else:
                display_title = f"{base_title} {part_number}"
                
            self.stdout.write(f"  └── NOUVELLE Lesson \"{display_title}\" (sera créée)")
            self.stdout.write(f"      └── NOUVEAU ContentLesson \"{content_lesson.title_en}\" - {len(group)} mots")
            
            # Afficher quelques exemples de ce groupe
            sample_size = min(3, len(group))
            samples = random.sample(group, sample_size) if len(group) >= sample_size else group
            
            for word in samples:
                self.stdout.write(f"          ├── {word.word_en}: {word.definition_en[:40]}...")
                
            if len(group) > sample_size:
                self.stdout.write(f"          └── ...et {len(group) - sample_size} autres mots")
        
        # Actions qui seront exécutées
        self.stdout.write("\nACTIONS QUI SERONT EXÉCUTÉES:")
        action_num = 1
        
        # Renommage si nécessaire
        if first_title != original_title:
            self.stdout.write(f"{action_num}. Renommage de la leçon existante en \"{first_title}\"")
            action_num += 1
            
        self.stdout.write(f"{action_num}. Conservation de {len(groups[0])} mots dans le ContentLesson original (ID={content_lesson.id})")
        action_num += 1
        
        for i in range(1, len(groups)):
            part_number = i + 1
            display_title = second_title if i == 1 and second_number is not None else f"{base_title} {part_number}"
            
            # Déterminer l'unité cible pour cette partie
            target_unit = target_units_map.get(part_number, default_target_unit) if target_units_map else default_target_unit
            self.stdout.write(f"{action_num}. Création d'une nouvelle leçon \"{display_title}\" dans l'Unité {target_unit.order} ({target_unit.title_en})")
            self.stdout.write(f"   Création d'un nouveau ContentLesson avec {len(groups[i])} mots")
            action_num += 1

    def _export_vocabulary_for_validation(self, vocabulary, export_file, parts):
        """Exporte le vocabulaire dans un fichier CSV pour validation manuelle"""
        with open(export_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Écrire l'en-tête
            writer.writerow(['id', 'word_en', 'definition_en', 'word_type_en', 'group'])
            
            # Écrire chaque mot avec une proposition de groupe
            items_per_part = len(vocabulary) // parts
            for i, word in enumerate(vocabulary):
                group = min(parts, (i // items_per_part) + 1)
                writer.writerow([word.id, word.word_en, word.definition_en[:40], word.word_type_en, group])

    def _import_validation_file(self, import_file, original_vocabulary):
        """Importe un fichier de validation CSV avec la répartition des mots"""
        # Créer un dictionnaire pour accéder rapidement aux objets vocabulaire par ID
        vocab_dict = {str(word.id): word for word in original_vocabulary}
        
        groups = []
        max_group = 0
        
        with open(import_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Trouver le nombre de groupes
            for row in reader:
                group = int(row.get('group', 0))
                max_group = max(max_group, group)
                
        # Réinitialiser le fichier pour le relire
        with open(import_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Initialiser les groupes
            groups = [[] for _ in range(max_group)]
            
            # Remplir les groupes selon le fichier
            for row in reader:
                word_id = row.get('id')
                group = int(row.get('group', 0)) - 1  # Convertir en index 0-based
                
                if word_id in vocab_dict and 0 <= group < max_group:
                    groups[group].append(vocab_dict[word_id])
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Ignoré: mot ID {word_id} ou groupe {group+1} invalide"
                    ))
                    
        # Vérifier si tous les mots ont été traités
        all_words = set()
        for group in groups:
            for word in group:
                all_words.add(word.id)
                
        for word in original_vocabulary:
            if word.id not in all_words:
                self.stdout.write(self.style.WARNING(f"Mot non traité: {word.id} - {word.word_en}"))
                
        return groups

    def _create_matching_exercise(self, content_lesson, vocabulary_items):
        """Crée un exercice de matching pour une leçon de vocabulaire"""
        # Chercher s'il existe déjà une leçon de matching
        matching_lesson = ContentLesson.objects.filter(
            lesson=content_lesson.lesson,
            content_type__icontains='matching'
        ).first()
        
        # Créer la leçon de matching si elle n'existe pas
        if not matching_lesson:
            max_order = ContentLesson.objects.filter(
                lesson=content_lesson.lesson
            ).aggregate(max_order=models.Max('order'))['max_order'] or 0
            
            matching_lesson = ContentLesson.objects.create(
                lesson=content_lesson.lesson,
                content_type='matching',
                title_en=f"Matching Exercise - {content_lesson.title_en}",
                title_fr=f"Exercice d'association - {content_lesson.title_fr}",
                title_es=f"Ejercicio de emparejamiento - {content_lesson.title_es}",
                title_nl=f"Koppelenoefening - {content_lesson.title_nl}",
                instruction_en="Match the words with their translations",
                instruction_fr="Associez les mots avec leurs traductions",
                instruction_es="Relaciona las palabras con sus traducciones",
                instruction_nl="Koppel de woorden aan hun vertalingen",
                estimated_duration=5,
                order=max_order + 1
            )
            
        # Créer l'exercice de matching
        # WITHOUT specifying the ID to let the database generate it automatically
        exercise = MatchingExercise.objects.create(
            content_lesson=matching_lesson,
            title_en=f"Match vocabulary from {content_lesson.lesson.title_en}",
            title_fr=f"Associez le vocabulaire de {content_lesson.lesson.title_fr}",
            title_es=f"Empareja el vocabulario de {content_lesson.lesson.title_es}",
            title_nl=f"Koppel woordenschat van {content_lesson.lesson.title_nl}",
            pairs_count=min(10, len(vocabulary_items)),
            difficulty='medium'
        )
        
        # Associer le vocabulaire à l'exercice
        exercise.vocabulary_words.set(vocabulary_items[:exercise.pairs_count])
        
        self.stdout.write(f"Créé un exercice de matching avec {exercise.pairs_count} paires")
        
        return exercise

    def _reorganize_lesson_order(self, lesson, new_content_lessons):
        """Réorganise l'ordre des leçons de contenu après une division"""
        # Récupérer toutes les leçons de contenu de cette leçon
        all_content_lessons = ContentLesson.objects.filter(lesson=lesson).order_by('order')
        
        # Réorganiser avec un incrément de 10 pour permettre des ajouts futurs
        for i, cl in enumerate(all_content_lessons):
            new_order = (i + 1) * 10
            if cl.order != new_order:
                cl.order = new_order
                cl.save()
                
        self.stdout.write(f"Réorganisé {all_content_lessons.count()} leçons de contenu")

    def _manually_select_words(self, vocabulary, parts):
        """Permet à l'utilisateur de sélectionner manuellement les mots pour chaque partie"""
        groups = [[] for _ in range(parts)]
        remaining_words = vocabulary.copy()
        
        self.stdout.write(self.style.SUCCESS(f"\n=== Sélection manuelle des mots pour {parts} parties ===\n"))
        self.stdout.write("Vous allez sélectionner les mots pour chaque partie, une par une.")
        self.stdout.write("Les mots restants non assignés seront automatiquement attribués à la dernière partie.")
        
        # Afficher toutes les options disponibles pour l'utilisateur
        self.stdout.write(self.style.WARNING("\nOptions disponibles:"))
        self.stdout.write("- Entrez les numéros des mots séparés par des virgules (ex: 1,3,5,7)")
        self.stdout.write("- Utilisez des tirets pour sélectionner des plages (ex: 1-5,8,10-12)")
        self.stdout.write("- Entrez 'voir' pour réafficher la liste des mots disponibles")
        self.stdout.write("- Entrez 'annuler' pour annuler la dernière sélection")
        self.stdout.write("- Entrez 'complet' pour voir la sélection complète actuelle")
        self.stdout.write("- Entrez 'skip' pour passer à la partie suivante (sans sélection)")
        self.stdout.write("- Entrez 'auto' pour distribuer automatiquement les mots restants")
        self.stdout.write("- Entrez 'aide' pour afficher cette aide\n")
        
        for part in range(parts - 1):  # Nous sélectionnons pour toutes les parties sauf la dernière
            part_number = part + 1
            self.stdout.write(self.style.WARNING(f"\n--- Sélection pour la Partie {part_number}/{parts} ---"))
            
            # Afficher les mots disponibles avec leurs indices
            self._display_available_words(remaining_words)
                
            while True:
                # Demander à l'utilisateur de sélectionner les mots
                self.stdout.write("\nEntrez les indices des mots à inclure (séparés par des virgules)")
                self.stdout.write("Exemple: 1,3,5,7 ou 1-5,8,10-12 (ou 'aide' pour les options)")
                user_input = input("Sélection: ").strip()
                
                # Traiter les commandes spéciales
                if user_input.lower() == 'skip':
                    break
                elif user_input.lower() == 'aide':
                    self.stdout.write(self.style.WARNING("\nOptions disponibles:"))
                    self.stdout.write("- Entrez les numéros des mots séparés par des virgules (ex: 1,3,5,7)")
                    self.stdout.write("- Utilisez des tirets pour sélectionner des plages (ex: 1-5,8,10-12)")
                    self.stdout.write("- Entrez 'voir' pour réafficher la liste des mots disponibles")
                    self.stdout.write("- Entrez 'annuler' pour annuler la dernière sélection")
                    self.stdout.write("- Entrez 'complet' pour voir la sélection complète actuelle")
                    self.stdout.write("- Entrez 'skip' pour passer à la partie suivante (sans sélection)")
                    self.stdout.write("- Entrez 'auto' pour distribuer automatiquement les mots restants")
                    self.stdout.write("- Entrez 'aide' pour afficher cette aide")
                    continue
                elif user_input.lower() == 'voir':
                    self._display_available_words(remaining_words)
                    continue
                elif user_input.lower() == 'complet':
                    self._display_current_selection(groups, part_number)
                    continue
                elif user_input.lower() == 'auto':
                    # Distribuer automatiquement les mots restants entre les parties restantes
                    remainder_parts = parts - part
                    words_per_part = len(remaining_words) // remainder_parts
                    
                    if words_per_part == 0:
                        self.stdout.write(self.style.ERROR("Pas assez de mots restants pour une distribution automatique"))
                        continue
                        
                    selected_words = remaining_words[:words_per_part]
                    groups[part].extend(selected_words)
                    
                    remaining_words = remaining_words[words_per_part:]
                    self.stdout.write(self.style.SUCCESS(
                        f"Distribution automatique: {len(selected_words)} mots ajoutés à la Partie {part_number}"
                    ))
                    break
                elif user_input.lower() == 'annuler':
                    if not groups[part]:
                        self.stdout.write(self.style.WARNING("Aucune sélection à annuler pour cette partie"))
                        continue
                        
                    # Remettre les mots dans la liste des mots disponibles
                    last_selections = groups[part]
                    remaining_words.extend(last_selections)
                    groups[part] = []
                    
                    self.stdout.write(self.style.SUCCESS(f"Sélection annulée: {len(last_selections)} mots remis dans la liste"))
                    self._display_available_words(remaining_words)
                    continue
                elif not user_input:
                    continue
                    
                # Traiter l'entrée utilisateur pour la sélection de mots
                try:
                    selected_indices = self._parse_selection_input(user_input, len(remaining_words))
                    
                    if not selected_indices:
                        self.stdout.write(self.style.ERROR("Aucun indice valide trouvé dans l'entrée"))
                        continue
                        
                    # Vérifier les indices en dehors de la plage
                    invalid_indices = [idx for idx in selected_indices if idx < 0 or idx >= len(remaining_words)]
                    if invalid_indices:
                        self.stdout.write(self.style.ERROR(
                            f"Indices invalides: {[idx+1 for idx in invalid_indices]} "
                            f"(plage valide: 1-{len(remaining_words)})"
                        ))
                        continue
                    
                    # Ajouter les mots sélectionnés à la partie actuelle
                    selected_words = [remaining_words[idx] for idx in selected_indices]
                    groups[part].extend(selected_words)
                    
                    # Afficher un aperçu de la sélection
                    self.stdout.write("\nMots sélectionnés:")
                    for word in selected_words[:5]:  # Limiter à 5 exemples
                        self.stdout.write(f"- {word.word_en}: {word.definition_en[:40]}...")
                    if len(selected_words) > 5:
                        self.stdout.write(f"... et {len(selected_words) - 5} autres mots")
                    
                    # Retirer les mots sélectionnés de la liste des mots restants
                    remaining_words = [word for i, word in enumerate(remaining_words) 
                                      if i not in selected_indices]
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"\nAjouté {len(selected_words)} mots à la Partie {part_number}. "
                        f"{len(remaining_words)} mots restants."
                    ))
                    
                    # Demander si l'utilisateur veut continuer à ajouter des mots ou passer à la partie suivante
                    if remaining_words:
                        continue_adding = input("\nContinuer à ajouter des mots à cette partie? [y/N] ")
                        if continue_adding.lower() != 'y':
                            break
                    else:
                        self.stdout.write(self.style.WARNING("Tous les mots ont été sélectionnés."))
                        break
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur de traitement: {str(e)}"))
        
        # Ajouter tous les mots restants à la dernière partie
        groups[parts-1].extend(remaining_words)
        self.stdout.write(self.style.SUCCESS(f"Ajouté {len(remaining_words)} mots restants à la Partie {parts}"))
        
        # Afficher un résumé détaillé de la répartition
        self._display_selection_summary(groups)
        
        # Demander confirmation finale
        confirm = input("\nConfirmer cette répartition? [Y/n] ")
        if confirm.lower() == 'n':
            self.stdout.write(self.style.WARNING("Répartition annulée. Veuillez recommencer."))
            return self._manually_select_words(vocabulary, parts)
            
        return groups
        
    def _parse_selection_input(self, user_input, max_items):
        """Analyse l'entrée utilisateur pour extraire les indices de sélection"""
        selected_indices = []
        
        for segment in user_input.split(','):
            segment = segment.strip()
            if not segment:
                continue
                
            if '-' in segment:
                # Plage d'indices (ex: "1-5")
                try:
                    start, end = segment.split('-')
                    start_idx = int(start.strip()) - 1  # Ajuster pour l'index 0-based
                    end_idx = int(end.strip())  # Non ajusté car range exclut la dernière valeur
                    
                    # Vérifier que la plage est valide
                    if start_idx < 0:
                        self.stdout.write(self.style.ERROR(f"Indice de début invalide: {start}"))
                        continue
                    if end_idx > max_items:
                        self.stdout.write(self.style.WARNING(
                            f"Indice de fin ({end}) dépasse le maximum ({max_items}), ajusté"
                        ))
                        end_idx = max_items
                        
                    if start_idx >= end_idx:
                        self.stdout.write(self.style.ERROR(
                            f"Plage invalide: {segment} (le début doit être inférieur à la fin)"
                        ))
                        continue
                        
                    selected_indices.extend(range(start_idx, end_idx))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Format de plage invalide: {segment}"))
            else:
                # Indice unique
                try:
                    idx = int(segment) - 1  # Ajuster pour l'index 0-based
                    if 0 <= idx < max_items:
                        selected_indices.append(idx)
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"Indice hors limites: {segment} (doit être entre 1 et {max_items})"
                        ))
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Indice invalide: {segment}"))
        
        # Supprimer les doublons et trier
        return sorted(set(selected_indices))
        
    def _display_available_words(self, words):
        """Affiche les mots disponibles avec leurs indices"""
        if not words:
            self.stdout.write(self.style.WARNING("Aucun mot disponible."))
            return
            
        self.stdout.write("\nMots disponibles:")
        
        # Déterminer le nombre de colonnes en fonction du nombre de mots
        # Plus de 20 mots -> affichage en 2 colonnes pour économiser l'espace
        columns = 2 if len(words) > 20 else 1
        items_per_column = (len(words) + columns - 1) // columns
        
        if columns == 1:
            # Affichage simple en une colonne
            for i, word in enumerate(words):
                self.stdout.write(f"{i+1:3d}. {word.word_en:<20}: {word.definition_en[:40]}...")
        else:
            # Affichage en plusieurs colonnes
            for i in range(items_per_column):
                line = ""
                for col in range(columns):
                    idx = i + col * items_per_column
                    if idx < len(words):
                        word = words[idx]
                        # Ajouter du padding pour aligner les colonnes
                        item_text = f"{idx+1:3d}. {word.word_en:<15}: {word.definition_en[:25]}..."
                        line += f"{item_text:<50}"
                self.stdout.write(line)
                
        self.stdout.write(f"\nTotal: {len(words)} mots disponibles")
        
    def _display_current_selection(self, groups, current_part):
        """Affiche la sélection actuelle pour toutes les parties"""
        self.stdout.write("\n=== Sélection actuelle ===")
        
        for i, group in enumerate(groups):
            if i + 1 == current_part:
                status = "(en cours)"
            elif i + 1 > current_part:
                status = "(à venir)"
            else:
                status = "(terminé)"
                
            self.stdout.write(f"Partie {i+1}: {len(group)} mots {status}")
            
            # Afficher les mots pour cette partie
            if group:
                for j, word in enumerate(group[:5]):  # Limiter à 5 exemples
                    self.stdout.write(f"  {j+1}. {word.word_en}: {word.definition_en[:40]}...")
                if len(group) > 5:
                    self.stdout.write(f"  ... et {len(group) - 5} autres mots")
        
    def _display_selection_summary(self, groups):
        """Affiche un résumé détaillé de la répartition finale"""
        self.stdout.write("\n=== Résumé de la répartition manuelle ===")
        
        total_words = sum(len(group) for group in groups)
        
        for i, group in enumerate(groups):
            part_number = i + 1
            percentage = (len(group) / total_words * 100) if total_words > 0 else 0
            
            self.stdout.write(self.style.SUCCESS(
                f"Partie {part_number}: {len(group)} mots ({percentage:.1f}%)"
            ))
            
            # Afficher quelques exemples de mots pour chaque partie
            sample_size = min(5, len(group))
            for j, word in enumerate(group[:sample_size]):
                self.stdout.write(f"  {j+1}. {word.word_en}: {word.definition_en[:40]}...")
            
            if len(group) > sample_size:
                self.stdout.write(f"  ... et {len(group) - sample_size} autres mots")
                
        # Indicateur d'équilibre
        sizes = [len(group) for group in groups]
        min_size = min(sizes) if sizes else 0
        max_size = max(sizes) if sizes else 0
        
        if max_size - min_size <= 2:
            balance = "excellente"
        elif max_size - min_size <= 5:
            balance = "bonne"
        elif max_size - min_size <= 10:
            balance = "acceptable"
        else:
            balance = "déséquilibrée"
            
        self.stdout.write(f"\nÉquilibre de la répartition: {balance} (écart max: {max_size - min_size} mots)")
        self.stdout.write(f"Total: {total_words} mots répartis en {len(groups)} parties")

    def _group_by_theme(self, vocabulary, parts):
        """Regroupe le vocabulaire par thème ou similarité en utilisant plusieurs stratégies"""
        self.stdout.write("Groupement thématique avancé en cours...")
        
        # Stratégie 1: Essayer de regrouper par champs sémantiques en utilisant les définitions
        # Créer un dictionnaire de mots clés courants pour différents thèmes
        themes = {
            "transport": ["car", "bus", "train", "drive", "vehicle", "transport", "road", "travel", "journey"],
            "food": ["food", "eat", "drink", "meal", "restaurant", "kitchen", "cook", "taste", "fruit", "vegetable"],
            "home": ["house", "home", "room", "furniture", "family", "live", "apartment", "building"],
            "work": ["work", "job", "office", "company", "business", "career", "profession", "employee"],
            "education": ["school", "learn", "study", "student", "teacher", "education", "university", "course"],
            "nature": ["tree", "plant", "animal", "nature", "environment", "forest", "river", "mountain"],
            "technology": ["computer", "phone", "device", "technology", "internet", "digital", "app", "software"],
            "health": ["health", "body", "doctor", "hospital", "medical", "disease", "pain", "healthy"],
            "people": ["person", "people", "man", "woman", "child", "family", "friend", "relationship"],
            "clothes": ["wear", "clothes", "dress", "shoe", "fashion", "outfit", "clothing", "garment"],
            "time": ["time", "hour", "day", "week", "month", "year", "date", "calendar", "schedule"],
            "entertainment": ["movie", "music", "game", "play", "fun", "entertainment", "sport", "hobby"],
        }
        
        # Créer des groupes pour chaque partie
        groups = [[] for _ in range(parts)]
        
        # Fonction pour trouver le thème d'un mot
        def find_theme(word):
            # Chercher dans la définition et le mot lui-même
            text_to_search = (word.word_en + " " + word.definition_en).lower()
            matched_themes = {}
            
            for theme_name, keywords in themes.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_to_search:
                        score += 1
                if score > 0:
                    matched_themes[theme_name] = score
            
            # Retourner le thème avec le meilleur score, ou None si aucun match
            if matched_themes:
                return max(matched_themes.items(), key=lambda x: x[1])[0]
            return None
        
        # Phase 1: Classification des mots par thème
        word_themes = {}
        unclassified_words = []
        
        for word in vocabulary:
            theme = find_theme(word)
            if theme:
                if theme not in word_themes:
                    word_themes[theme] = []
                word_themes[theme].append(word)
            else:
                # Fallback sur le type de mot comme avant
                word_type = word.word_type_en.lower()
                theme_key = f"type_{word_type}"
                if theme_key not in word_themes:
                    word_themes[theme_key] = []
                word_themes[theme_key].append(word)
        
        # Phase 2: Répartition équitable des thèmes entre les groupes
        # Trier les thèmes par nombre de mots (décroissant)
        sorted_themes = sorted(word_themes.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Afficher un résumé de la classification
        self.stdout.write("Classification thématique des mots:")
        for theme, words in sorted_themes:
            self.stdout.write(f" - {theme}: {len(words)} mots")
        
        # Répartir les plus gros thèmes en premier
        for theme, words in sorted_themes:
            # Si le thème est très grand, répartir ses mots entre les groupes
            if len(words) > len(vocabulary) // parts // 2:
                words_per_group = len(words) // parts
                for i in range(parts):
                    start = i * words_per_group
                    end = start + words_per_group if i < parts - 1 else len(words)
                    groups[i].extend(words[start:end])
            else:
                # Sinon, mettre tout le thème dans le groupe le moins rempli
                group_index = min(range(parts), key=lambda i: len(groups[i]))
                groups[group_index].extend(words)
        
        # Phase 3: Équilibrage final
        # Vérifier si les groupes sont équilibrés
        target_size = len(vocabulary) // parts
        for i in range(parts - 1):
            # Si un groupe est trop grand, déplacer des mots vers le groupe suivant
            while len(groups[i]) > target_size + 2 and len(groups[i+1]) < target_size - 2:
                groups[i+1].append(groups[i].pop())
                
        # Afficher les statistiques finales
        self.stdout.write("Répartition finale des mots:")
        for i, group in enumerate(groups):
            self.stdout.write(f" - Partie {i+1}: {len(group)} mots")
        
        return groups