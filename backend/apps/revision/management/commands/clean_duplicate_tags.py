# apps/revision/management/commands/clean_duplicate_tags.py

from django.core.management.base import BaseCommand
from apps.revision.models import FlashcardDeck


class Command(BaseCommand):
    help = 'Nettoie les tags dupliqués case-insensitive dans tous les decks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait modifié sans appliquer les changements',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucune modification ne sera appliquée'))
        
        decks_modified = 0
        total_tags_removed = 0
        
        # Traiter tous les decks avec des tags
        decks_with_tags = FlashcardDeck.objects.exclude(tags__isnull=True).exclude(tags=[])
        
        self.stdout.write(f'Traitement de {decks_with_tags.count()} decks avec des tags...')
        
        for deck in decks_with_tags:
            if not deck.tags:
                continue
                
            original_tags = deck.tags.copy()
            original_count = len(original_tags)
            
            # Dédupliquer les tags case-insensitive en gardant la première occurrence
            seen_normalized = set()
            cleaned_tags = []
            
            for tag in original_tags:
                normalized = tag.strip().lower()
                if normalized and normalized not in seen_normalized:
                    seen_normalized.add(normalized)
                    cleaned_tags.append(tag.strip())  # Garder la casse originale mais nettoyer les espaces
            
            # Vérifier s'il y a eu des changements
            if len(cleaned_tags) != original_count or cleaned_tags != original_tags:
                decks_modified += 1
                tags_removed = original_count - len(cleaned_tags)
                total_tags_removed += tags_removed
                
                self.stdout.write(
                    f'Deck "{deck.name}" (ID: {deck.id}):',
                    ending=''
                )
                self.stdout.write(
                    f'  - Avant: {original_tags}',
                    ending=''
                )
                self.stdout.write(
                    f'  - Après: {cleaned_tags}',
                    ending=''
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  - {tags_removed} tag(s) dupliqué(s) supprimé(s)')
                )
                
                if not dry_run:
                    deck.tags = cleaned_tags
                    deck.save()
        
        # Résumé
        if decks_modified > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Nettoyage terminé: {decks_modified} deck(s) modifié(s), '
                    f'{total_tags_removed} tag(s) dupliqué(s) supprimé(s)'
                )
            )
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('Pour appliquer les changements, exécutez sans --dry-run')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Aucun doublon de tags trouvé - la base de données est propre!')
            )