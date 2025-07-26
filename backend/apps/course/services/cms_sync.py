"""
Service de synchronisation entre CMS et Course app.
Importe les cours publiés du CMS vers le marketplace Course.
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from typing import List, Dict, Any
from ..models.core import Unit

logger = logging.getLogger(__name__)

class CMSSyncService:
    """Service pour synchroniser les cours du CMS vers le marketplace Course."""
    
    def __init__(self):
        self.cms_base_url = getattr(settings, 'CMS_BASE_URL', 'http://127.0.0.1:8002')
        self.cms_api_key = getattr(settings, 'CMS_API_KEY', None)
    
    def sync_published_courses(self) -> Dict[str, Any]:
        """
        Synchronise tous les cours publiés du CMS vers Course app.
        
        Returns:
            Dict avec le résultat de la synchronisation (created, updated, errors)
        """
        result = {
            'created': 0,
            'updated': 0,
            'errors': [],
            'total_processed': 0
        }
        
        try:
            # Récupérer les cours publiés du CMS
            published_courses = self._fetch_published_courses()
            result['total_processed'] = len(published_courses)
            
            for cms_course in published_courses:
                try:
                    with transaction.atomic():
                        unit, created = self._sync_single_course(cms_course)
                        if created:
                            result['created'] += 1
                        else:
                            result['updated'] += 1
                            
                except Exception as e:
                    error_msg = f"Error syncing course {cms_course.get('id', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            logger.info(f"CMS Sync completed: {result}")
            
        except Exception as e:
            error_msg = f"Failed to fetch courses from CMS: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def _fetch_published_courses(self) -> List[Dict[str, Any]]:
        """
        Récupère les cours publiés depuis le CMS.
        
        Returns:
            Liste des cours publiés
        """
        # Pour l'instant, simulation des données
        # Dans une vraie implémentation, ceci ferait un appel API au CMS
        
        # Simulation de données CMS
        mock_courses = [
            {
                'id': 1,
                'teacher_id': 1,
                'teacher_name': 'Marie Dupont',
                'title_en': 'French for Beginners',
                'title_fr': 'Français pour Débutants',
                'title_es': 'Francés para Principiantes',
                'title_nl': 'Frans voor Beginners',
                'description_en': 'Learn French from scratch with interactive lessons',
                'description_fr': 'Apprenez le français depuis zéro avec des leçons interactives',
                'description_es': 'Aprende francés desde cero con lecciones interactivas',
                'description_nl': 'Leer Frans vanaf nul met interactieve lessen',
                'level': 'A1',
                'order': 1,
                'price': 49.99,
                'is_published': True,
                'is_free': False,
                'created_at': '2025-01-15T10:00:00Z',
                'updated_at': '2025-01-20T15:30:00Z'
            },
            {
                'id': 2,
                'teacher_id': 1,
                'teacher_name': 'Marie Dupont', 
                'title_en': 'Intermediate French Conversation',
                'title_fr': 'Conversation Française Intermédiaire',
                'title_es': 'Conversación Francesa Intermedia',
                'title_nl': 'Tussenliggend Frans Gesprek',
                'description_en': 'Improve your French speaking skills',
                'description_fr': 'Améliorez vos compétences orales en français',
                'description_es': 'Mejora tus habilidades de habla francesa',
                'description_nl': 'Verbeter je Franse sprekvaardigheden',
                'level': 'B1',
                'order': 2,
                'price': 79.99,
                'is_published': True,
                'is_free': False,
                'created_at': '2025-01-16T11:00:00Z',
                'updated_at': '2025-01-21T16:30:00Z'
            },
            {
                'id': 3,
                'teacher_id': 2,
                'teacher_name': 'John Smith',
                'title_en': 'Free English Grammar Basics',
                'title_fr': 'Bases de Grammaire Anglaise Gratuite',
                'title_es': 'Fundamentos Gratuitos de Gramática Inglesa',
                'title_nl': 'Gratis Engelse Grammatica Basis',
                'description_en': 'Master English grammar with free exercises',
                'description_fr': 'Maîtrisez la grammaire anglaise avec des exercices gratuits',
                'description_es': 'Domina la gramática inglesa con ejercicios gratuitos',
                'description_nl': 'Beheers Engelse grammatica met gratis oefeningen',
                'level': 'A2',
                'order': 1,
                'price': 0.00,
                'is_published': True,
                'is_free': True,
                'created_at': '2025-01-17T12:00:00Z',
                'updated_at': '2025-01-22T17:30:00Z'
            }
        ]
        
        return mock_courses
    
    def _sync_single_course(self, cms_course: Dict[str, Any]) -> tuple:
        """
        Synchronise un seul cours du CMS vers Course app.
        
        Args:
            cms_course: Données du cours depuis le CMS
            
        Returns:
            Tuple (Unit, created) où created est un boolean
        """
        cms_unit_id = cms_course['id']
        
        # Chercher si le cours existe déjà
        unit, created = Unit.objects.update_or_create(
            cms_unit_id=cms_unit_id,
            defaults={
                'teacher_id': cms_course['teacher_id'],
                'teacher_name': cms_course['teacher_name'],
                'title_en': cms_course['title_en'],
                'title_fr': cms_course['title_fr'],
                'title_es': cms_course['title_es'],
                'title_nl': cms_course['title_nl'],
                'description_en': cms_course.get('description_en', ''),
                'description_fr': cms_course.get('description_fr', ''),
                'description_es': cms_course.get('description_es', ''),
                'description_nl': cms_course.get('description_nl', ''),
                'level': cms_course['level'],
                'order': cms_course['order'],
                'price': cms_course['price'],
                'is_published': cms_course['is_published'],
                'is_free': cms_course['is_free'],
                'last_sync': timezone.now()
            }
        )
        
        return unit, created
    
    def sync_single_course_by_id(self, cms_unit_id: int) -> Dict[str, Any]:
        """
        Synchronise un cours spécifique par son ID CMS.
        
        Args:
            cms_unit_id: ID du cours dans le CMS
            
        Returns:
            Dict avec le résultat de la synchronisation
        """
        try:
            # Dans une vraie implémentation, récupérer depuis l'API CMS
            # Pour l'instant, simuler
            cms_course = None
            published_courses = self._fetch_published_courses()
            
            for course in published_courses:
                if course['id'] == cms_unit_id:
                    cms_course = course
                    break
            
            if not cms_course:
                return {'success': False, 'error': f'Course {cms_unit_id} not found in CMS'}
            
            unit, created = self._sync_single_course(cms_course)
            
            return {
                'success': True,
                'created': created,
                'unit_id': unit.id,
                'title': unit.title
            }
            
        except Exception as e:
            logger.error(f"Error syncing course {cms_unit_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

def sync_cms_courses():
    """Function helper pour synchroniser les cours depuis une commande Django."""
    service = CMSSyncService()
    return service.sync_published_courses()