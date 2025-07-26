"""
Commande Django pour synchroniser les cours du CMS vers le marketplace Course.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.course.services.cms_sync import CMSSyncService

class Command(BaseCommand):
    help = 'Synchronise les cours publiés du CMS vers le marketplace Course'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            help='Synchroniser un cours spécifique par son ID CMS'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler la synchronisation sans modifier la base de données'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'🔄 Début de la synchronisation CMS → Course à {timezone.now()}')
        )
        
        service = CMSSyncService()
        
        if options['course_id']:
            # Synchroniser un cours spécifique
            course_id = options['course_id']
            self.stdout.write(f'📚 Synchronisation du cours ID: {course_id}')
            
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('⚠️  Mode simulation - aucune modification ne sera effectuée'))
                return
            
            result = service.sync_single_course_by_id(course_id)
            
            if result['success']:
                status = 'créé' if result['created'] else 'mis à jour'
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Cours "{result["title"]}" {status} avec succès')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur: {result["error"]}')
                )
        else:
            # Synchroniser tous les cours publiés
            self.stdout.write('📚 Synchronisation de tous les cours publiés...')
            
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('⚠️  Mode simulation - aucune modification ne sera effectuée'))
                # Simuler en récupérant juste les données
                published_courses = service._fetch_published_courses()
                self.stdout.write(f'📊 {len(published_courses)} cours trouvés dans le CMS')
                for course in published_courses:
                    self.stdout.write(f'  - {course["title_fr"]} (ID: {course["id"]}) - {course["teacher_name"]}')
                return
            
            result = service.sync_published_courses()
            
            # Afficher les résultats
            self.stdout.write('\n📊 Résultats de la synchronisation:')
            self.stdout.write(f'   📈 Cours traités: {result["total_processed"]}')
            self.stdout.write(f'   ✨ Nouveaux cours: {result["created"]}')
            self.stdout.write(f'   🔄 Cours mis à jour: {result["updated"]}')
            
            if result['errors']:
                self.stdout.write(f'   ❌ Erreurs: {len(result["errors"])}')
                for error in result['errors']:
                    self.stdout.write(f'      - {error}')
            else:
                self.stdout.write('   ✅ Aucune erreur')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Synchronisation terminée à {timezone.now()}')
        )