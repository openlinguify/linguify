# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from . import models
from . import profile
from . import email_models

# Export des modèles principaux pour la compatibilité
from .models import *
from .email_models import *
from ..utils.validators import *