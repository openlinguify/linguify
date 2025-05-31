
import os
import sys
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from apps.course.models import Unit
from django.db import connection

# Check database connection
print('Database:', connection.settings_dict['NAME'])
print('Host:', connection.settings_dict['HOST'])

# Check if Unit model can access database
try:
    count = Unit.objects.count()
    print(f'Current units count: {count}')
    
    # Create a test unit if none exist
    if count == 0:
        unit = Unit.objects.create(
            title_en='Test Unit English',
            title_fr='Unité Test Français', 
            title_es='Unidad de Prueba Español',
            title_nl='Test Eenheid Nederlands',
            description_en='Test description',
            description_fr='Description de test',
            description_es='Descripción de prueba', 
            description_nl='Test beschrijving',
            level='A1',
            order=1
        )
        print(f'Created test unit: {unit.id}')
        
    print(f'Final units count: {Unit.objects.count()}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

