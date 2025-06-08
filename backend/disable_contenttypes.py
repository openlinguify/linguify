import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
from django.conf import settings

# Disable contenttypes signals temporarily
settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != 'django.contrib.contenttypes']

django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'migrate'])