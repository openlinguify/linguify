"""
Management command pour migrer les cartes existantes vers le système adaptatif.
Crée des CardMastery pour toutes les cartes et initialise les scores de confiance.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.revision.models import Flashcard, CardMastery
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Migre les cartes existantes vers le système d\'apprentissage adaptatif'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=int,
            help='ID d\'utilisateur spécifique (optionnel)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans appliquer les changements',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_id = options.get('user')

        self.stdout.write(self.style.WARNING('=== Migration vers le système adaptatif ===\n'))

        # Filtrer les cartes
        cards_query = Flashcard.objects.all()
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                cards_query = cards_query.filter(user=user)
                self.stdout.write(f"Filtrage pour l'utilisateur: {user.username}\n")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Utilisateur avec ID {user_id} introuvable"))
                return

        total_cards = cards_query.count()
        self.stdout.write(f"Nombre total de cartes à migrer: {total_cards}\n")

        if total_cards == 0:
            self.stdout.write(self.style.WARNING("Aucune carte à migrer"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("MODE DRY-RUN - Aucune modification ne sera appliquée\n"))

        # Statistiques
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        with transaction.atomic():
            for card in cards_query.select_related('deck'):
                try:
                    # Vérifier si CardMastery existe déjà
                    mastery, created = CardMastery.objects.get_or_create(
                        card=card,
                        defaults={
                            'confidence_score': self._estimate_initial_confidence(card),
                            'total_attempts': card.review_count,
                            'successful_attempts': card.correct_reviews_count,
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            f"  [+] Cree CardMastery pour '{card.front_text[:30]}...' "
                            f"(confidence: {mastery.confidence_score}%)"
                        )
                    else:
                        # Si existe déjà, on peut le mettre à jour si nécessaire
                        if mastery.total_attempts == 0 and card.review_count > 0:
                            mastery.total_attempts = card.review_count
                            mastery.successful_attempts = card.correct_reviews_count
                            mastery.confidence_score = self._estimate_initial_confidence(card)
                            mastery.save()
                            updated_count += 1
                            self.stdout.write(
                                f"  [U] Mis a jour CardMastery pour '{card.front_text[:30]}...'"
                            )
                        else:
                            skipped_count += 1

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  [!] Erreur pour carte {card.id}: {str(e)}")
                    )

            if dry_run:
                # Annuler la transaction en mode dry-run
                transaction.set_rollback(True)

        # Afficher le résumé
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"\n[OK] Migration terminee!\n"))
        self.stdout.write(f"  Crees:      {created_count}")
        self.stdout.write(f"  Mis a jour: {updated_count}")
        self.stdout.write(f"  Ignores:    {skipped_count}")
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"  Erreurs:    {error_count}"))
        self.stdout.write("")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[!] Mode DRY-RUN - Aucune modification appliquee"))
        else:
            self.stdout.write(self.style.SUCCESS("\n[OK] Modifications enregistrees dans la base de donnees"))

    def _estimate_initial_confidence(self, card):
        """
        Estime un score de confiance initial basé sur les données existantes.

        Args:
            card (Flashcard): La carte à évaluer

        Returns:
            int: Score de confiance estimé (0-100)
        """
        # Si la carte est marquée comme apprise
        if card.learned:
            # Base de 70% pour les cartes apprises
            base_score = 70

            # Ajouter des points selon le nombre de révisions
            if card.review_count >= 10:
                base_score += 15
            elif card.review_count >= 5:
                base_score += 10
            elif card.review_count >= 3:
                base_score += 5

            # Ajouter des points selon le taux de réussite
            if card.total_reviews_count > 0:
                success_rate = card.correct_reviews_count / card.total_reviews_count
                base_score += int(success_rate * 15)

            return min(base_score, 100)

        # Si la carte n'est pas apprise
        else:
            # Calculer selon le taux de réussite
            if card.total_reviews_count > 0:
                success_rate = card.correct_reviews_count / card.total_reviews_count
                estimated = int(success_rate * 60)  # Max 60% si pas learned
                return max(estimated, 10)  # Minimum 10%
            else:
                # Carte jamais révisée
                return 0