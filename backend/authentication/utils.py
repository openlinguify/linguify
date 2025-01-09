# backend/django_apps/authentication/utils.py
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
import json

import jwt
import requests

from django.contrib.auth import authenticate
from django.core.mail import send_mail


def notify_coach_of_commission_change(coach_profile):
    """
    Notify the coach that their commission rate has been changed.
    """
    coach_email = coach_profile.user.email
    subject = "Important Update: Your Commission Rate Has Changed"
    message = (
        f"Dear {coach_profile.user.first_name},\n\n"
        "We hope this message finds you well.\n\n"
        "We are reaching out to let you know that your commission rate has recently been updated.\n\n"
        "Here are the details of this update:\n"
        "---------------------------------------------------\n"
        "- New Commission Rate: Please log in to view details\n"
        "- Effective Date: Effective immediately\n"
        "---------------------------------------------------\n\n"
        "To view the new commission rate and learn more about how it affects your earnings, please visit your coach profile here:\n"
        "👉 [View My Profile](https://platform.com/coach/profile)\n\n"
        "If you have any questions or concerns about this update, please feel free to reach out to us. We are here to ensure that your experience on our platform remains smooth and transparent.\n\n"
        "Thank you for your continued dedication and the positive impact you bring to your students. We sincerely appreciate having you as a valuable part of our community.\n\n"
        "Warm regards,\n"
        "The Platform Team"
    )
    send_mail(subject, message, 'noreply@platform.com', [coach_email])

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format('dev-hazi5dwwkk7pe476.eu.auth0.com')).json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = 'https://{}/'.format('dev-hazi5dwwkk7pe476.eu.auth0.com')
    return jwt.decode(token, public_key, audience='https://dev-hazi5dwwkk7pe476.eu.auth0.com/api/v2/', issuer=issuer, algorithms=['RS256'])


