#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import translation
from django.utils.translation import gettext as _
from apps.authentication.models.models import User

# Test user language
user = User.objects.get(username='admin')
print(f"User language in DB: {user.interface_language}")

# Test translation activation
translation.activate('fr')
print(f"Active language: {translation.get_language()}")

# Test some translations
test_strings = [
    "Profile picture",
    "Personal Information",
    "Interface Language",
    "Privacy & Security",
    "Learning Preferences",
    "Notifications & Reminders"
]

print("\nTranslations test:")
for text in test_strings:
    translated = _(text)
    print(f"  {text} -> {translated}")

# Check locale paths
from django.conf import settings
print(f"\nLocale paths configured: {settings.LOCALE_PATHS}")
print(f"Languages available: {settings.LANGUAGES}")
print(f"USE_I18N: {settings.USE_I18N}")