# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

default_app_config = 'apps.authentication.apps.AuthenticationConfig'

# Ne pas importer les modules au niveau de l'app pour éviter les imports circulaires
# Les imports se feront à la demande dans les autres modules