import os
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from backend.apps.authentication.utils.helpers import clean_temp_profile_pictures
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    """
    Commande Django pour nettoyer les photos de profil temporaires et optimiser le stockage.
    
    Usage: python manage.py cleanup_profile_pictures [--days=7] [--temp-hours=24] [--force]
    """
    help = 'Nettoie les photos de profil temporaires et optimise le stockage'
    
    def add_arguments(self, parser):
        # Âge maximum pour les versions historiques (jours)
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Nombre de jours à conserver pour les versions historiques'
        )
        
        # Âge maximum pour les fichiers temporaires (heures)
        parser.add_argument(
            '--temp-hours',
            type=int,
            default=24,
            help='Nombre d\'heures à conserver pour les fichiers temporaires'
        )
        
        # Option pour forcer le nettoyage sans confirmation
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer le nettoyage sans demander de confirmation'
        )
        
        # Nettoyer pour un utilisateur spécifique
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID utilisateur spécifique à nettoyer'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        temp_hours = options['temp_hours']
        force = options['force']
        user_id = options.get('user_id')
        
        # Confirmation si --force n'est pas utilisé
        if not force:
            confirm = input(f"Voulez-vous nettoyer les photos de profil temporaires > {temp_hours}h et les versions historiques > {days} jours ? [y/N] ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Nettoyage annulé."))
                return
        
        # 1. Nettoyer les fichiers temporaires
        self.stdout.write("Nettoyage des fichiers temporaires...")
        temp_age_seconds = temp_hours * 3600
        result = clean_temp_profile_pictures(max_age=temp_age_seconds)
        
        if result['status'] == 'completed':
            self.stdout.write(self.style.SUCCESS(
                f"Nettoyage des fichiers temporaires terminé. "
                f"{result['deleted_count']} fichiers supprimés, "
                f"{result['error_count']} erreurs."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"Nettoyage des fichiers temporaires ignoré : {result.get('reason', 'raison inconnue')}"
            ))
        
        # 2. Nettoyer les versions historiques
        self.stdout.write("Nettoyage des versions historiques...")
        
        # Calculer la date limite
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count = 0
        error_count = 0
        
        # Si un utilisateur spécifique est demandé
        if user_id:
            try:
                users = User.objects.filter(id=user_id)
                if not users.exists():
                    self.stdout.write(self.style.ERROR(f"Utilisateur avec ID {user_id} non trouvé."))
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors de la recherche de l'utilisateur {user_id}: {e}"))
                return
        else:
            # Tous les utilisateurs avec des photos de profil
            users = User.objects.exclude(profile_picture='')
        
        # Traiter chaque utilisateur
        for user in users:
            user_id = str(user.id)
            user_original_dir = os.path.join(settings.MEDIA_ROOT, 'profiles', user_id, 'original')
            
            if not os.path.exists(user_original_dir):
                continue
            
            # Lister et trier les fichiers (format: timestamp_uuid.ext)
            try:
                files = []
                for filename in os.listdir(user_original_dir):
                    file_path = os.path.join(user_original_dir, filename)
                    
                    # Ignorer les répertoires
                    if not os.path.isfile(file_path):
                        continue
                    
                    # Obtenir l'horodatage du fichier
                    try:
                        # Essayer d'extraire le timestamp du nom de fichier
                        timestamp_part = filename.split('_')[0]
                        timestamp = int(timestamp_part)
                    except (ValueError, IndexError):
                        # Sinon utiliser la date de modification
                        timestamp = int(os.path.getmtime(file_path))
                    
                    files.append((file_path, timestamp, filename))
                
                # Trier par timestamp (du plus récent au plus ancien)
                files.sort(key=lambda x: x[1], reverse=True)
                
                # Conserver le fichier le plus récent et supprimer les anciens au-delà de la date limite
                for i, (file_path, timestamp, filename) in enumerate(files):
                    # Toujours conserver au moins un fichier
                    if i == 0:
                        continue
                    
                    # Convertir le timestamp en datetime pour comparer avec la date limite
                    file_date = timezone.datetime.fromtimestamp(timestamp, tz=timezone.get_current_timezone())
                    
                    # Supprimer si plus ancien que la date limite
                    if file_date < cutoff_date:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            self.stdout.write(f"Suppression de {file_path}")
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f"Erreur lors de la suppression de {file_path}: {e}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors du traitement de l'utilisateur {user_id}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Nettoyage terminé. {deleted_count} fichiers historiques supprimés, {error_count} erreurs."
        ))