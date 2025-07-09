# backend/apps/revision/tests/__init__.py

# Import all test modules to make them discoverable by Django test runner

from .test_simple import *
from .test_models import *
from .test_views_api import *
from .test_serializers import *
from .test_permissions import *
from .test_integration import *
from .test_tags import *
from .test_learning_settings import *
from .test_learning_integration import *
from .test_learning_edge_cases import *
from .test_learning_viewsets import *