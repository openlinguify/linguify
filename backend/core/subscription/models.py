# backend/core/subscription/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import stripe


class SubscriptionPlan(models.Model):
    """Plans d'abonnement disponibles"""

    PLAN_TYPES = [
        ('free', 'Gratuit'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]

    name = models.CharField(max_length=50, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Limitations par plan
    max_workspaces = models.IntegerField(default=1)
    max_flashcard_decks = models.IntegerField(default=10)
    max_ai_conversations_per_month = models.IntegerField(default=50)
    has_premium_courses = models.BooleanField(default=False)
    has_video_coaching = models.BooleanField(default=False)
    has_certificates = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['price_monthly']

    def __str__(self):
        return f"{self.name} - {self.price_monthly}€/mois"


class UserSubscription(models.Model):
    """Abonnement utilisateur actuel"""

    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('canceled', 'Annulé'),
        ('past_due', 'Impayé'),
        ('unpaid', 'Non payé'),
        ('incomplete', 'Incomplet'),
        ('trialing', 'Période d\'essai'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)

    # Stripe fields
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Dates importantes
    started_at = models.DateTimeField(default=timezone.now)
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    trial_end = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)

    # Usage tracking
    ai_conversations_this_month = models.IntegerField(default=0)
    last_usage_reset = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    @property
    def is_active(self):
        """Vérifie si l'abonnement est actif"""
        return self.status in ['active', 'trialing']

    @property
    def is_premium(self):
        """Vérifie si l'utilisateur a un plan premium ou plus"""
        return self.plan.plan_type in ['premium', 'pro']

    @property
    def is_pro(self):
        """Vérifie si l'utilisateur a le plan pro"""
        return self.plan.plan_type == 'pro'

    def can_create_workspace(self):
        """Vérifie si l'utilisateur peut créer un nouveau workspace"""
        # Pour l'instant, pas de modèle workspace, on assume 1 par défaut
        return self.plan.max_workspaces == -1 or self.plan.max_workspaces > 1

    def can_use_ai_chat(self):
        """Vérifie si l'utilisateur peut utiliser l'IA ce mois"""
        if self.plan.max_ai_conversations_per_month == -1:  # Illimité
            return True
        self._reset_monthly_usage_if_needed()
        return self.ai_conversations_this_month < self.plan.max_ai_conversations_per_month

    def increment_ai_usage(self):
        """Incrémente l'usage IA du mois"""
        self._reset_monthly_usage_if_needed()
        self.ai_conversations_this_month += 1
        self.save(update_fields=['ai_conversations_this_month'])

    def _reset_monthly_usage_if_needed(self):
        """Reset les compteurs usage si nouveau mois"""
        now = timezone.now()
        if (now.year != self.last_usage_reset.year or
            now.month != self.last_usage_reset.month):
            self.ai_conversations_this_month = 0
            self.last_usage_reset = now
            self.save(update_fields=['ai_conversations_this_month', 'last_usage_reset'])


class PaymentHistory(models.Model):
    """Historique des paiements"""

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('succeeded', 'Réussi'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_history'
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=100)
    stripe_invoice_id = models.CharField(max_length=100, blank=True, null=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    # Metadata
    description = models.CharField(max_length=200, blank=True)
    billing_period_start = models.DateTimeField(blank=True, null=True)
    billing_period_end = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.amount}€ - {self.status}"


# Fonction utilitaire pour créer les plans par défaut
def create_default_plans():
    """Crée les plans d'abonnement par défaut"""

    plans_data = [
        {
            'name': 'Gratuit',
            'plan_type': 'free',
            'price_monthly': Decimal('0.00'),
            'price_yearly': Decimal('0.00'),
            'max_workspaces': 1,
            'max_flashcard_decks': 10,
            'max_ai_conversations_per_month': 50,
            'has_premium_courses': False,
            'has_video_coaching': False,
            'has_certificates': False,
            'has_api_access': False,
            'has_priority_support': False,
        },
        {
            'name': 'Premium',
            'plan_type': 'premium',
            'price_monthly': Decimal('9.99'),
            'price_yearly': Decimal('99.99'),
            'max_workspaces': 5,
            'max_flashcard_decks': 100,
            'max_ai_conversations_per_month': 500,
            'has_premium_courses': True,
            'has_video_coaching': False,
            'has_certificates': True,
            'has_api_access': False,
            'has_priority_support': True,
        },
        {
            'name': 'Pro',
            'plan_type': 'pro',
            'price_monthly': Decimal('19.99'),
            'price_yearly': Decimal('199.99'),
            'max_workspaces': -1,  # Illimité
            'max_flashcard_decks': -1,  # Illimité
            'max_ai_conversations_per_month': -1,  # Illimité
            'has_premium_courses': True,
            'has_video_coaching': True,
            'has_certificates': True,
            'has_api_access': True,
            'has_priority_support': True,
        }
    ]

    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"Plan créé: {plan.name}")