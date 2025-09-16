# backend/core/subscription/admin.py
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, PaymentHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'price_monthly', 'price_yearly',
        'max_workspaces', 'max_ai_conversations_per_month', 'is_active'
    ]
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'plan_type', 'is_active')
        }),
        ('Pricing Stripe', {
            'fields': ('stripe_price_id', 'price_monthly', 'price_yearly')
        }),
        ('Limitations', {
            'fields': (
                'max_workspaces', 'max_flashcard_decks',
                'max_ai_conversations_per_month'
            )
        }),
        ('Fonctionnalités', {
            'fields': (
                'has_premium_courses', 'has_video_coaching',
                'has_certificates', 'has_api_access', 'has_priority_support'
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan', 'status', 'stripe_subscription_id',
        'current_period_end', 'ai_conversations_this_month'
    ]
    list_filter = ['plan__plan_type', 'status', 'started_at']
    search_fields = ['user__email', 'user__username', 'stripe_customer_id']
    readonly_fields = [
        'stripe_subscription_id', 'stripe_customer_id',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['user']

    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id')
        }),
        ('Dates', {
            'fields': (
                'started_at', 'current_period_start', 'current_period_end',
                'trial_end', 'canceled_at'
            )
        }),
        ('Usage', {
            'fields': ('ai_conversations_this_month', 'last_usage_reset')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount', 'currency', 'status',
        'stripe_payment_intent_id', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'user__email', 'stripe_payment_intent_id',
        'stripe_invoice_id', 'description'
    ]
    readonly_fields = [
        'stripe_payment_intent_id', 'stripe_invoice_id', 'created_at'
    ]
    raw_id_fields = ['user', 'subscription']

    fieldsets = (
        ('Transaction', {
            'fields': ('user', 'subscription', 'amount', 'currency', 'status')
        }),
        ('Stripe', {
            'fields': ('stripe_payment_intent_id', 'stripe_invoice_id')
        }),
        ('Détails', {
            'fields': (
                'description', 'billing_period_start', 'billing_period_end'
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'subscription')