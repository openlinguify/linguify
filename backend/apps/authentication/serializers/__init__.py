# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from . import user_serializers
from . import profile_serializers
from . import auth_serializers
from . import settings_serializers

# Export des serializers pour la compatibilité
from .settings_serializers import (
    UserSerializer, UserRegistrationSerializer, MeSerializer, 
    ProfileUpdateSerializer, GeneralSettingsSerializer, 
    CookieConsentSerializer, CookieConsentCreateSerializer,
    NotificationSettingsSerializer, LearningSettingsSerializer,
    PrivacySettingsSerializer, AppearanceSettingsSerializer,
    PasswordChangeSerializer, TermsAcceptanceSerializer
)
from .profile_serializers import ProfileSerializer
from .user_serializers import *
from .auth_serializers import *