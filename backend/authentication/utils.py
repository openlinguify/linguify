# backend/django_apps/authentication/utils.py
from django.conf import settings

import json

import jwt
import requests

from django.contrib.auth import authenticate


def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get(f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json').json()
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    issuer = f'https://{settings.AUTH0_DOMAIN}/'
    return jwt.decode(token, public_key, 
                     audience=settings.AUTH0_AUDIENCE,
                     issuer=issuer,
                     algorithms=['RS256'])

