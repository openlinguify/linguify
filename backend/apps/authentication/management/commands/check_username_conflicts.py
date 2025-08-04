"""
Commande Django pour vérifier et résoudre les conflits de usernames case-insensitive
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import Lower

User = get_user_model()


class Command(BaseCommand):
    help = 'Vérifie et résout les conflits de usernames case-insensitive'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrige automatiquement les conflits en ajoutant des suffixes',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test - montre ce qui serait fait sans appliquer les modifications',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Vérification des conflits de usernames case-insensitive...")
        
        # Trouver les usernames en conflit (même nom en minuscules)
        conflicts = (
            User.objects
            .values(lower_username=Lower('username'))
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .order_by('lower_username')
        )
        
        if not conflicts:
            self.stdout.write(
                self.style.SUCCESS("✅ Aucun conflit détecté ! Tous les usernames sont uniques (insensible à la casse).")
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f"⚠️  {len(conflicts)} conflit(s) détecté(s) :")
        )
        
        total_users_affected = 0
        
        for conflict in conflicts:
            lower_username = conflict['lower_username']
            count = conflict['count']
            
            # Récupérer tous les utilisateurs avec ce username (case-insensitive)
            conflicting_users = User.objects.filter(username__iexact=lower_username).order_by('id')
            
            self.stdout.write(f"\n📛 Conflit pour '{lower_username}' ({count} utilisateurs) :")
            
            for i, user in enumerate(conflicting_users):
                marker = "🏆 GARDÉ" if i == 0 else "🔄 À MODIFIER"
                self.stdout.write(f"   {marker} ID: {user.id} | Username: '{user.username}' | Email: {user.email}")
                if i > 0:
                    total_users_affected += 1
        
        if options['fix'] or options['dry_run']:
            mode = "🧪 MODE TEST" if options['dry_run'] else "🔧 CORRECTION"
            self.stdout.write(f"\n{mode} - Résolution des conflits...")
            
            fixed_count = 0
            
            for conflict in conflicts:
                lower_username = conflict['lower_username']
                conflicting_users = User.objects.filter(username__iexact=lower_username).order_by('id')
                
                # Garder le premier (par ID), modifier les autres
                for i, user in enumerate(conflicting_users[1:], 1):
                    old_username = user.username
                    new_username = f"{user.username}_{i}"
                    
                    # Vérifier que le nouveau username n'existe pas déjà
                    while User.objects.filter(username__iexact=new_username).exists():
                        i += 1
                        new_username = f"{user.username}_{i}"
                    
                    if not options['dry_run']:
                        user.username = new_username
                        user.save()
                    
                    self.stdout.write(
                        f"   ✅ {old_username} → {new_username} (ID: {user.id})"
                    )
                    fixed_count += 1
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f"\n🧪 Mode test terminé. {fixed_count} utilisateur(s) seraient modifiés.")
                )
                self.stdout.write("Exécutez sans --dry-run pour appliquer les modifications.")
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"\n✅ {fixed_count} username(s) corrigé(s) avec succès !")
                )
        
        else:
            self.stdout.write(
                f"\n📊 Résumé : {total_users_affected} utilisateur(s) doivent être modifiés."
            )
            self.stdout.write("Utilisez --fix pour corriger automatiquement.")
            self.stdout.write("Utilisez --dry-run pour voir ce qui serait fait.")
        
        self.stdout.write("\n💡 Conseil : Après correction, appliquez la migration pour ajouter la contrainte.")