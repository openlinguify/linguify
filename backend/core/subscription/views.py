# backend/core/subscription/views.py
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .models import SubscriptionPlan, UserSubscription, PaymentHistory

logger = logging.getLogger(__name__)

# Configuration Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None


@login_required
def subscription_plans(request):
    """Affiche les plans d'abonnement disponibles"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    current_subscription = getattr(request.user, 'subscription', None)

    context = {
        'plans': plans,
        'current_subscription': current_subscription,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
    }
    return render(request, 'subscription/plans.html', context)


@login_required
def create_checkout_session(request, plan_id):
    """Crée une session Stripe Checkout"""
    if not stripe.api_key:
        messages.error(request, "Le système de paiement n'est pas configuré.")
        return redirect('subscription:plans')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Ne pas permettre de s'abonner au plan gratuit
    if plan.plan_type == 'free':
        messages.info(request, "Vous êtes déjà sur le plan gratuit.")
        return redirect('subscription:plans')

    try:
        # Créer ou récupérer le customer Stripe
        customer = None
        if hasattr(request.user, 'subscription') and request.user.subscription.stripe_customer_id:
            customer_id = request.user.subscription.stripe_customer_id
            try:
                customer = stripe.Customer.retrieve(customer_id)
            except stripe.error.InvalidRequestError:
                customer = None

        if not customer:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name(),
                metadata={'user_id': request.user.id}
            )

        # Créer la session checkout
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri(
                reverse('subscription:success') + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri(reverse('subscription:plans')),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
            }
        )

        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Erreur Stripe: {e}")
        messages.error(request, "Erreur lors de la création de la session de paiement.")
        return redirect('subscription:plans')


@login_required
def subscription_success(request):
    """Page de confirmation après paiement réussi"""
    session_id = request.GET.get('session_id')

    if session_id and stripe.api_key:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                messages.success(request, "Votre abonnement a été activé avec succès!")
            else:
                messages.warning(request, "Votre paiement est en cours de traitement.")
        except stripe.error.StripeError:
            messages.info(request, "Votre abonnement a été traité.")

    return render(request, 'subscription/success.html')


@login_required
def manage_subscription(request):
    """Page de gestion de l'abonnement utilisateur"""
    try:
        subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        # Créer un abonnement gratuit par défaut
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        subscription = UserSubscription.objects.create(
            user=request.user,
            plan=free_plan
        )

    context = {
        'subscription': subscription,
        'payment_history': subscription.payments.all()[:10] if subscription else [],
    }
    return render(request, 'subscription/manage.html', context)


@csrf_exempt
def stripe_webhook(request):
    """Webhook pour les événements Stripe"""
    if not stripe.api_key:
        return HttpResponse(status=400)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error("Invalid payload dans webhook Stripe")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature dans webhook Stripe")
        return HttpResponse(status=400)

    # Traiter l'événement
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_cancelled(event['data']['object'])

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Traite la completion d'une session checkout"""
    try:
        user_id = session['metadata']['user_id']
        plan_id = session['metadata']['plan_id']

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Récupérer la subscription Stripe
        stripe_subscription = stripe.Subscription.retrieve(session['subscription'])

        # Créer ou mettre à jour l'abonnement utilisateur
        subscription, created = UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan,
                'stripe_subscription_id': stripe_subscription.id,
                'stripe_customer_id': session['customer'],
                'status': stripe_subscription.status,
                'current_period_start': timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start, tz=timezone.utc
                ),
                'current_period_end': timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end, tz=timezone.utc
                ),
            }
        )

        logger.info(f"Abonnement {'créé' if created else 'mis à jour'} pour l'utilisateur {user.email}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de checkout.session.completed: {e}")


def handle_payment_succeeded(invoice):
    """Traite un paiement réussi"""
    try:
        subscription_id = invoice['subscription']
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)

        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )

        # Enregistrer le paiement
        PaymentHistory.objects.create(
            user=user_subscription.user,
            subscription=user_subscription,
            stripe_payment_intent_id=invoice['payment_intent'],
            stripe_invoice_id=invoice['id'],
            amount=invoice['amount_paid'] / 100,  # Stripe utilise des centimes
            currency=invoice['currency'].upper(),
            status='succeeded',
            description=f"Paiement {user_subscription.plan.name}",
            billing_period_start=timezone.datetime.fromtimestamp(
                invoice['period_start'], tz=timezone.utc
            ),
            billing_period_end=timezone.datetime.fromtimestamp(
                invoice['period_end'], tz=timezone.utc
            ),
        )

        logger.info(f"Paiement enregistré pour {user_subscription.user.email}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de invoice.payment_succeeded: {e}")


def handle_subscription_updated(stripe_subscription):
    """Traite la mise à jour d'un abonnement"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )

        user_subscription.status = stripe_subscription['status']
        user_subscription.current_period_start = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_start'], tz=timezone.utc
        )
        user_subscription.current_period_end = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_end'], tz=timezone.utc
        )

        if stripe_subscription.get('canceled_at'):
            user_subscription.canceled_at = timezone.datetime.fromtimestamp(
                stripe_subscription['canceled_at'], tz=timezone.utc
            )

        user_subscription.save()

        logger.info(f"Abonnement mis à jour pour {user_subscription.user.email}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de customer.subscription.updated: {e}")


def handle_subscription_cancelled(stripe_subscription):
    """Traite l'annulation d'un abonnement"""
    try:
        user_subscription = UserSubscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )

        # Repasser au plan gratuit
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        user_subscription.plan = free_plan
        user_subscription.status = 'canceled'
        user_subscription.canceled_at = timezone.now()
        user_subscription.save()

        logger.info(f"Abonnement annulé pour {user_subscription.user.email}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de customer.subscription.deleted: {e}")


# API Views pour usage dans les apps
class SubscriptionAPI(View):
    """API pour vérifier les limitations d'abonnement"""

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            subscription = request.user.subscription
            return JsonResponse({
                'plan': subscription.plan.plan_type,
                'is_premium': subscription.is_premium,
                'is_pro': subscription.is_pro,
                'can_use_ai': subscription.can_use_ai_chat(),
                'ai_usage': subscription.ai_conversations_this_month,
                'ai_limit': subscription.plan.max_ai_conversations_per_month,
            })
        except UserSubscription.DoesNotExist:
            return JsonResponse({
                'plan': 'free',
                'is_premium': False,
                'is_pro': False,
                'can_use_ai': True,
                'ai_usage': 0,
                'ai_limit': 50,
            })