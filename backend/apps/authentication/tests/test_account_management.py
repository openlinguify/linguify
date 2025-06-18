"""
Tests pour les fonctionnalités de gestion de compte dans l'application authentication.
Couvre notamment:
- La suppression de compte (immédiate et planifiée)
- L'annulation de suppression de compte
- L'acceptation des conditions d'utilisation
"""
import pytest
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAccountDeletion:
    """Tests pour les fonctionnalités de suppression de compte."""

    def test_schedule_account_deletion(self, create_user):
        """Test la planification de suppression d'un compte avec période de grâce."""
        user = create_user()
        
        # Vérification de l'état initial
        assert user.is_active is True
        assert user.is_pending_deletion is False
        assert user.deletion_scheduled_at is None
        assert user.deletion_date is None
        
        # Planifier la suppression du compte
        result = user.schedule_account_deletion(days_retention=30)
        
        # Vérification de l'état après planification
        assert user.is_active is False
        assert user.is_pending_deletion is True
        assert user.deletion_scheduled_at is not None
        assert user.deletion_date is not None
        
        # Vérification des dates retournées par la méthode
        assert 'scheduled_at' in result
        assert 'deletion_date' in result
        
        # Vérification que la date de suppression est bien dans 30 jours
        delta = user.deletion_date - timezone.now()
        assert 29 <= delta.days <= 30

    def test_cancel_account_deletion(self, create_user):
        """Test l'annulation d'une suppression de compte planifiée."""
        user = create_user()
        
        # Planifier la suppression
        user.schedule_account_deletion()
        
        assert user.is_active is False
        assert user.is_pending_deletion is True
        
        # Annuler la suppression
        result = user.cancel_account_deletion()
        
        # Vérification que l'annulation a réussi
        assert result is True
        assert user.is_active is True
        assert user.is_pending_deletion is False
        assert user.deletion_scheduled_at is None
        assert user.deletion_date is None

    def test_cancel_account_deletion_not_pending(self, create_user):
        """Test l'annulation d'une suppression pour un compte qui n'est pas en attente de suppression."""
        user = create_user()
        
        # Le compte n'est pas en attente de suppression
        assert user.is_pending_deletion is False
        
        # Tenter d'annuler la suppression
        result = user.cancel_account_deletion()
        
        # L'annulation retourne False car il n'y a pas de suppression en attente
        assert result is False
        assert user.is_active is True

    def test_days_until_deletion(self, create_user):
        """Test le calcul du nombre de jours restants avant suppression."""
        user = create_user()
        
        # Sans suppression planifiée
        assert user.days_until_deletion() is None
        
        # Planifier la suppression
        user.schedule_account_deletion(days_retention=15)
        
        # Vérifier le nombre de jours restants
        days_remaining = user.days_until_deletion()
        assert days_remaining is not None
        assert 14 <= days_remaining <= 15

    def test_delete_user_account_immediate(self, create_user):
        """Test la suppression immédiate d'un compte."""
        user = create_user()
        user_id = user.id
        
        # Supprimer immédiatement
        result = user.delete_user_account(anonymize=True, immediate=True)
        assert result is True
        
        # Vérifier que l'utilisateur a bien été supprimé
        assert User.objects.filter(id=user_id).count() == 0

    def test_delete_user_account_schedule(self, create_user):
        """Test la planification de suppression via delete_user_account."""
        user = create_user()
        
        # Planifier la suppression
        result = user.delete_user_account(immediate=False)
        
        # Vérifier que la planification a réussi
        assert 'scheduled_at' in result
        assert 'deletion_date' in result
        assert user.is_pending_deletion is True
        assert user.is_active is False


@pytest.mark.django_db
class TestTermsAcceptance:
    """Tests pour les fonctionnalités d'acceptation des conditions d'utilisation."""

    def test_terms_acceptance(self, create_user):
        """Test l'acceptation des conditions d'utilisation."""
        user = create_user()
        
        # État initial
        assert user.terms_accepted is False
        assert user.terms_accepted_at is None
        assert user.terms_version == 'v1.0'  # Valeur par défaut
        
        # Accepter les conditions avec une version spécifique
        result = user.accept_terms(version='v2.0')
        
        # Vérification que l'acceptation a réussi
        assert result is True
        assert user.terms_accepted is True
        assert user.terms_accepted_at is not None
        assert user.terms_version == 'v2.0'
        
        # Vérifier que la date d'acceptation est récente
        time_diff = timezone.now() - user.terms_accepted_at
        assert time_diff.seconds < 10  # L'acceptation a eu lieu il y a moins de 10 secondes


@pytest.mark.django_db
class TestUserValidation:
    """Tests pour les validations du modèle utilisateur."""

    def test_native_target_language_validation(self, create_user):
        """Test la validation empêchant d'avoir la même langue native et cible."""
        user = create_user(native_language='FR', target_language='EN')
        
        # Tenter de définir la même langue native et cible
        with pytest.raises(ValidationError):
            user.update_profile(native_language='EN', target_language='EN')
        
        # Les valeurs originales doivent être conservées
        user.refresh_from_db()
        assert user.native_language == 'FR'
        assert user.target_language == 'EN'
        
        # Tenter de mettre à jour uniquement la langue cible pour qu'elle corresponde à la langue native
        with pytest.raises(ValidationError):
            user.update_profile(target_language='FR')
        
        # Tenter de mettre à jour uniquement la langue native pour qu'elle corresponde à la langue cible
        with pytest.raises(ValidationError):
            user.update_profile(native_language='EN')