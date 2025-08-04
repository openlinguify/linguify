"""
Système de synergies entre applications éducatives
Gère les interactions et partages de données entre 100+ apps
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from django.core.cache import cache
from .app_registry import get_app_registry

logger = logging.getLogger(__name__)

class SynergyType(Enum):
    """Types de synergies entre apps"""
    DATA_SHARING = "data_sharing"           # Partage de données
    WORKFLOW_CHAIN = "workflow_chain"       # Chaîne pédagogique
    CONTENT_ENRICHMENT = "content_enrichment"  # Enrichissement de contenu
    PROGRESS_TRACKING = "progress_tracking"    # Suivi de progression
    SKILL_CORRELATION = "skill_correlation"   # Corrélation de compétences
    USER_PREFERENCE = "user_preference"       # Préférences utilisateur

@dataclass
class SynergyConnection:
    """Représente une connexion de synergie entre deux apps"""
    source_app: str
    target_app: str
    synergy_type: SynergyType
    data_flow: Dict[str, Any]
    strength: float  # 0.0 à 1.0
    bidirectional: bool = False
    
class AppSynergyManager:
    """
    Gestionnaire des synergies entre applications éducatives
    """
    
    def __init__(self):
        self.registry = get_app_registry()
        self.cache_timeout = 1800  # 30 minutes
        
    def discover_synergies(self, force_refresh: bool = False) -> Dict[str, List[SynergyConnection]]:
        """
        Découvre automatiquement les synergies entre toutes les apps
        """
        cache_key = "linguify_app_synergies"
        
        if not force_refresh:
            cached_synergies = cache.get(cache_key)
            if cached_synergies:
                return cached_synergies
        
        logger.info("Discovering app synergies...")
        all_apps = self.registry.discover_all_apps()
        synergies = {}
        
        for app_code in all_apps.keys():
            synergies[app_code] = self._find_app_synergies(app_code, all_apps)
        
        # Mettre en cache
        cache.set(cache_key, synergies, self.cache_timeout)
        logger.info(f"Discovered synergies for {len(synergies)} apps")
        
        return synergies
    
    def _find_app_synergies(self, app_code: str, all_apps: Dict) -> List[SynergyConnection]:
        """Trouve les synergies pour une app spécifique"""
        app_info = all_apps.get(app_code)
        if not app_info:
            return []
        
        connections = []
        
        for other_code, other_info in all_apps.items():
            if other_code == app_code:
                continue
                
            # Analyser chaque type de synergie
            for synergy_type in SynergyType:
                connection = self._analyze_synergy(app_code, app_info, other_code, other_info, synergy_type)
                if connection and connection.strength > 0.3:  # Seuil minimum
                    connections.append(connection)
        
        return sorted(connections, key=lambda x: x.strength, reverse=True)
    
    def _analyze_synergy(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict, 
                        synergy_type: SynergyType) -> Optional[SynergyConnection]:
        """Analyse un type de synergie spécifique entre deux apps"""
        
        if synergy_type == SynergyType.DATA_SHARING:
            return self._analyze_data_sharing(app1, app1_info, app2, app2_info)
        elif synergy_type == SynergyType.WORKFLOW_CHAIN:
            return self._analyze_workflow_chain(app1, app1_info, app2, app2_info)
        elif synergy_type == SynergyType.CONTENT_ENRICHMENT:
            return self._analyze_content_enrichment(app1, app1_info, app2, app2_info)
        elif synergy_type == SynergyType.PROGRESS_TRACKING:
            return self._analyze_progress_tracking(app1, app1_info, app2, app2_info)
        elif synergy_type == SynergyType.SKILL_CORRELATION:
            return self._analyze_skill_correlation(app1, app1_info, app2, app2_info)
        elif synergy_type == SynergyType.USER_PREFERENCE:
            return self._analyze_user_preference(app1, app1_info, app2, app2_info)
        
        return None
    
    def _analyze_data_sharing(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse les possibilités de partage de données"""
        strength = 0.0
        data_flow = {}
        
        # Apps avec API peuvent partager des données
        if 'api' in app1_info.get('capabilities', []) and 'api' in app2_info.get('capabilities', []):
            strength += 0.3
            data_flow['api_sharing'] = True
        
        # Apps de même catégorie partagent souvent des données
        if app1_info.get('category') == app2_info.get('category'):
            strength += 0.2
            data_flow['category_match'] = True
        
        # Dépendances directes
        if app2 in app1_info.get('dependencies', []):
            strength += 0.5
            data_flow['dependency'] = True
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.DATA_SHARING,
                data_flow=data_flow,
                strength=min(strength, 1.0)
            )
        return None
    
    def _analyze_workflow_chain(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse les chaînes de workflow pédagogique"""
        strength = 0.0
        data_flow = {}
        
        # Définir les chaînes pédagogiques typiques
        learning_chains = {
            'language_learning': ['course', 'vocabulary', 'revision', 'quiz', 'speaking'],
            'content_creation': ['notebook', 'ai_assistant', 'export', 'sharing'],
            'assessment': ['quiz', 'revision', 'progress_tracking', 'certification'],
            'communication': ['chat', 'community', 'collaboration', 'feedback']
        }
        
        for chain_name, chain_apps in learning_chains.items():
            if app1 in chain_apps and app2 in chain_apps:
                # Calculer la proximité dans la chaîne
                pos1 = chain_apps.index(app1)
                pos2 = chain_apps.index(app2)
                distance = abs(pos1 - pos2)
                
                if distance == 1:  # Apps adjacentes
                    strength += 0.8
                elif distance == 2:  # Apps proches
                    strength += 0.5
                elif distance <= 4:  # Apps dans la même chaîne
                    strength += 0.3
                
                data_flow['chain'] = chain_name
                data_flow['distance'] = distance
                break
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.WORKFLOW_CHAIN,
                data_flow=data_flow,
                strength=min(strength, 1.0),
                bidirectional=True
            )
        return None
    
    def _analyze_content_enrichment(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse l'enrichissement de contenu mutuel"""
        strength = 0.0
        data_flow = {}
        
        # Apps qui peuvent enrichir le contenu d'autres apps
        content_enrichers = {
            'language_ai': ['course', 'revision', 'quiz', 'notebook'],
            'vocabulary': ['course', 'revision', 'quiz'],
            'pronunciation': ['course', 'revision', 'speaking'],
            'community': ['course', 'revision', 'notebook'],
            'gamification': ['course', 'revision', 'quiz'],
        }
        
        for enricher, targets in content_enrichers.items():
            if app1 == enricher and app2 in targets:
                strength += 0.7
                data_flow['enrichment_type'] = f"{enricher}_to_{app2}"
                break
            elif app2 == enricher and app1 in targets:
                strength += 0.7
                data_flow['enrichment_type'] = f"{enricher}_to_{app1}"
                break
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.CONTENT_ENRICHMENT,
                data_flow=data_flow,
                strength=min(strength, 1.0)
            )
        return None
    
    def _analyze_progress_tracking(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse le suivi de progression croisé"""
        strength = 0.0
        data_flow = {}
        
        # Apps qui trackent la progression
        progress_trackers = ['course', 'revision', 'quiz', 'vocabulary', 'speaking']
        progress_consumers = ['dashboard', 'analytics', 'gamification', 'certification']
        
        if app1 in progress_trackers and app2 in progress_consumers:
            strength += 0.6
            data_flow['tracker_to_consumer'] = True
        elif app1 in progress_consumers and app2 in progress_trackers:
            strength += 0.6
            data_flow['consumer_from_tracker'] = True
        elif app1 in progress_trackers and app2 in progress_trackers:
            strength += 0.4
            data_flow['cross_tracking'] = True
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.PROGRESS_TRACKING,
                data_flow=data_flow,
                strength=min(strength, 1.0),
                bidirectional=True
            )
        return None
    
    def _analyze_skill_correlation(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse la corrélation des compétences"""
        strength = 0.0
        data_flow = {}
        
        # Compétences partagées entre apps
        skill_correlations = {
            ('course', 'vocabulary'): 0.8,
            ('course', 'revision'): 0.9,
            ('vocabulary', 'revision'): 0.8,
            ('speaking', 'pronunciation'): 0.9,
            ('writing', 'grammar'): 0.8,
            ('reading', 'comprehension'): 0.9,
            ('listening', 'pronunciation'): 0.7,
        }
        
        for (skill1, skill2), correlation in skill_correlations.items():
            if (app1 == skill1 and app2 == skill2) or (app1 == skill2 and app2 == skill1):
                strength = correlation
                data_flow['skill_correlation'] = correlation
                break
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.SKILL_CORRELATION,
                data_flow=data_flow,
                strength=strength,
                bidirectional=True
            )
        return None
    
    def _analyze_user_preference(self, app1: str, app1_info: Dict, app2: str, app2_info: Dict) -> Optional[SynergyConnection]:
        """Analyse le partage de préférences utilisateur"""
        strength = 0.0
        data_flow = {}
        
        # Apps qui partagent des préférences utilisateur similaires
        if app1_info.get('has_settings') and app2_info.get('has_settings'):
            strength += 0.4
            data_flow['shared_settings'] = True
        
        # Apps de même catégorie partagent souvent des préférences
        if app1_info.get('category') == app2_info.get('category'):
            strength += 0.3
            data_flow['category_preference'] = True
        
        if strength > 0:
            return SynergyConnection(
                source_app=app1,
                target_app=app2,
                synergy_type=SynergyType.USER_PREFERENCE,
                data_flow=data_flow,
                strength=min(strength, 1.0),
                bidirectional=True
            )
        return None
    
    def get_recommended_apps(self, user_apps: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recommande des apps basées sur les apps déjà utilisées
        """
        synergies = self.discover_synergies()
        recommendations = {}
        
        for user_app in user_apps:
            if user_app in synergies:
                for connection in synergies[user_app]:
                    target = connection.target_app
                    if target not in user_apps and target not in recommendations:
                        recommendations[target] = {
                            'app': target,
                            'total_strength': 0.0,
                            'connections': [],
                            'reasons': set()
                        }
                    
                    if target in recommendations:
                        recommendations[target]['total_strength'] += connection.strength
                        recommendations[target]['connections'].append(connection)
                        recommendations[target]['reasons'].add(connection.synergy_type.value)
        
        # Trier par force de recommandation
        sorted_recommendations = sorted(
            recommendations.values(),
            key=lambda x: x['total_strength'],
            reverse=True
        )
        
        return sorted_recommendations[:limit]
    
    def get_recommendations_for_user(self, user_apps: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Alias for get_recommended_apps for backward compatibility
        """
        return self.get_recommended_apps(user_apps, limit)
    
    def get_app_ecosystem_map(self) -> Dict[str, Any]:
        """
        Génère une carte de l'écosystème complet des apps
        """
        synergies = self.discover_synergies()
        all_apps = self.registry.discover_all_apps()
        
        ecosystem_map = {
            'nodes': [],
            'edges': [],
            'clusters': {},
            'statistics': {}
        }
        
        # Créer les nœuds (apps)
        for app_code, app_info in all_apps.items():
            ecosystem_map['nodes'].append({
                'id': app_code,
                'name': app_info.get('name', app_code),
                'category': app_info.get('category', 'Unknown'),
                'has_settings': app_info.get('has_settings', False),
                'capabilities': app_info.get('capabilities', []),
                'version': app_info.get('version', '1.0.0')
            })
        
        # Créer les arêtes (connexions)
        for app_code, connections in synergies.items():
            for connection in connections:
                if connection.strength > 0.5:  # Seuil pour la visualisation
                    ecosystem_map['edges'].append({
                        'source': connection.source_app,
                        'target': connection.target_app,
                        'strength': connection.strength,
                        'type': connection.synergy_type.value,
                        'bidirectional': connection.bidirectional
                    })
        
        # Calculer les statistiques
        ecosystem_map['statistics'] = {
            'total_apps': len(all_apps),
            'total_connections': sum(len(connections) for connections in synergies.values()),
            'avg_connections_per_app': sum(len(connections) for connections in synergies.values()) / len(all_apps) if all_apps else 0,
            'categories': list(set(app.get('category', 'Unknown') for app in all_apps.values())),
        }
        
        return ecosystem_map


# Instance globale
synergy_manager = AppSynergyManager()

def get_synergy_manager() -> AppSynergyManager:
    """Fonction utilitaire pour récupérer le gestionnaire de synergies"""
    return synergy_manager