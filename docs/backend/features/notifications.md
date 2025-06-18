# Système de Notifications Linguify

Le module de notifications offre une solution complète pour gérer les notifications utilisateur dans l'application Linguify. 
Cette documentation explique comment utiliser le système de notifications dans votre code.

## Types de Notifications Supportés

Le système supporte plusieurs types de notifications:

- `info` - Notifications informatives générales
- `success` - Notifications de succès (ex: action réussie)
- `warning` - Notifications d'avertissement
- `error` - Notifications d'erreur
- `lesson_reminder` - Rappels de leçons
- `flashcard` - Rappels de révision de flashcards
- `streak` - Notifications liées aux séries consécutives
- `achievement` - Accomplissements débloqués
- `system` - Notifications système
- `progress` - Notifications de progression

## Niveaux de Priorité

Chaque notification peut avoir un niveau de priorité:

- `low` - Basse priorité
- `medium` - Priorité moyenne (par défaut)
- `high` - Haute priorité

Les notifications de haute priorité seront toujours affichées à l'utilisateur, même pendant les heures de silence.

## Création de Notifications

Pour créer une notification dans votre code, utilisez le gestionnaire de notifications:

```python
from apps.notification.utils import NotificationManager

# Création d'une notification simple
NotificationManager.create_notification(
    user=user,
    title="Titre de la notification",
    message="Message détaillé de la notification",
    notification_type='info',
    priority='medium',
    data={"action": "view_profile"},  # Données optionnelles en JSON
    expires_in_days=7  # La notification expirera après 7 jours
)

# Pour les rappels de leçons
NotificationManager.send_lesson_reminder(
    user=user,
    lesson_title="Introduction à la grammaire",
    lesson_id=123,
    unit_id=45,
    unit_title="Bases de français"
)

# Pour les rappels de flashcards
NotificationManager.send_flashcard_reminder(
    user=user,
    due_count=15,  # Nombre de cartes à réviser
    deck_name="Vocabulaire essentiel",
    deck_id=789
)

# Pour les séries consécutives
NotificationManager.send_streak_notification(
    user=user,
    streak_days=7  # Nombre de jours consécutifs
)

# Pour les accomplissements
NotificationManager.send_achievement_notification(
    user=user,
    achievement_name="Maître linguiste",
    achievement_description="Vous avez complété 100 leçons!"
)

# Envoyer la même notification à plusieurs utilisateurs
users = User.objects.filter(is_active=True)
NotificationManager.send_bulk_notification(
    users=users,
    title="Nouvelle fonctionnalité disponible!",
    message="Découvrez notre nouveau module de révision interactive",
    notification_type='info',
    priority='medium',
    data={"action": "explore_features"},
    expires_in_days=14
)
```

## API REST pour les Notifications

Le système expose plusieurs endpoints REST pour interagir avec les notifications:

### Notifications

- `GET /api/v1/notifications/notifications/` - Liste toutes les notifications de l'utilisateur
- `GET /api/v1/notifications/notifications/unread/` - Liste seulement les notifications non lues
- `GET /api/v1/notifications/notifications/count_unread/` - Renvoie le nombre de notifications non lues
- `POST /api/v1/notifications/notifications/mark_all_read/` - Marque toutes les notifications comme lues
- `POST /api/v1/notifications/notifications/{id}/mark_read/` - Marque une notification spécifique comme lue
- `GET /api/v1/notifications/notifications/by_type/?type=lesson_reminder` - Filtre les notifications par type
- `DELETE /api/v1/notifications/notifications/clear_all/` - Supprime toutes les notifications

### Paramètres de Notifications

- `GET /api/v1/notifications/settings/` - Récupère les paramètres de notification de l'utilisateur
- `PATCH /api/v1/notifications/settings/update_settings/` - Met à jour les paramètres de notification

```json
{
  "email_enabled": true,
  "push_enabled": true,
  "web_enabled": true,
  "lesson_reminders": true,
  "flashcard_reminders": true,
  "achievement_notifications": true,
  "streak_notifications": true,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00"
}
```

### Appareils pour les Notifications Push

- `GET /api/v1/notifications/devices/` - Liste tous les appareils de l'utilisateur
- `POST /api/v1/notifications/devices/` - Enregistre un nouvel appareil
- `POST /api/v1/notifications/devices/{id}/activate/` - Active un appareil
- `POST /api/v1/notifications/devices/{id}/deactivate/` - Désactive un appareil
- `DELETE /api/v1/notifications/devices/remove_inactive/` - Supprime tous les appareils inactifs

## Notifications en Temps Réel

Le système utilise WebSockets pour les notifications en temps réel. Il s'appuie sur Redis comme backend de canal pour Django Channels.

### Configuration Redis

Pour utiliser Redis comme backend de canal, nous avons créé un fichier `docker-compose.redis.yml` :

```yaml
version: '3'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always
    networks:
      - linguify_network

networks:
  linguify_network:
    driver: bridge

volumes:
  redis_data:
    driver: local
```

Démarrez Redis avec la commande :

```bash
docker-compose -f docker-compose.redis.yml up -d
```

### Configuration Django

Dans `settings.py`, nous avons configuré Django Channels pour utiliser Redis :

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            # Use Redis from Docker Compose by default in development
            # or use environment variable for production
            "hosts": [(
                os.environ.get('REDIS_HOST', 'redis'), 
                int(os.environ.get('REDIS_PORT', 6379))
            )],
        },
    },
}
```

### Utilisation côté frontend

Voici comment se connecter aux WebSockets depuis le frontend :

```typescript
// Utilisation du service notificationWebsocket
import notificationWebsocket from '@/core/api/notificationWebsocket';

// Connexion avec le token d'authentification
const token = authService.getToken();
notificationWebsocket.connect(token);

// Écouter les notifications
notificationWebsocket.addListener((notification) => {
  console.log('Nouvelle notification reçue:', notification);
  // Ajouter la notification au state ou à la liste
});

// Écouter les changements d'état de connexion
notificationWebsocket.addConnectionListener((connected) => {
  console.log('État de connexion WebSocket:', connected ? 'connecté' : 'déconnecté');
});

// Pour fermer la connexion lors de la déconnexion
authService.onLogout(() => {
  notificationWebsocket.close();
});
```

Notre implémentation inclut également une gestion robuste des reconnexions en cas de perte de connexion.

## Architecture Frontend Améliorée

Nous avons récemment effectué un refactoring important du système de notifications côté frontend pour améliorer sa robustesse et sa maintenabilité :

### Centralisation des Types

Nous avons centralisé toutes les définitions de types dans un fichier unique `notification.types.ts` :

```typescript
// Types partagés pour le système de notification
export enum NotificationType {
  LESSON_REMINDER = 'lesson_reminder',
  SYSTEM = 'system',
  ACHIEVEMENT = 'achievement',
  REMINDER = 'reminder',
  FLASHCARD = 'flashcard',
  ANNOUNCEMENT = 'announcement',
}

export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  data?: any;
  isRead: boolean;
  createdAt: string;
  expiresAt?: string;
  actions?: NotificationAction[];
}

// Autres types...
```

### Services Découplés

Nous avons séparé les responsabilités dans des services distincts :

- `notificationStorage` : gestion du stockage des notifications
- `notificationLifecycle` : gestion du cycle de vie (expiration, nettoyage)
- `notificationManager` : opérations de haut niveau sur les notifications
- `notificationWebsocket` : connexion WebSocket pour les notifications en temps réel
- `notificationApi` : communication avec l'API backend
- `notificationService` : point d'entrée principal pour toutes les opérations

### Résolution des Dépendances Circulaires

Cette nouvelle architecture élimine les dépendances circulaires qui causaient des problèmes dans l'ancienne implémentation. Tous les services importent les types depuis le fichier centralisé, évitant ainsi les imports mutuels qui créaient des erreurs à l'exécution.

## Administration des Notifications

Le système inclut une interface d'administration complète pour gérer les notifications:

1. **Notifications**: Voir, filtrer et gérer toutes les notifications
2. **Paramètres de notification**: Gérer les paramètres de notification par utilisateur
3. **Appareils**: Voir et gérer les appareils enregistrés pour les notifications push

## Intégration avec d'autres modules

Pour intégrer le système de notifications avec d'autres modules, comme les leçons, les flashcards, etc., vous pouvez:

1. Importer `NotificationManager` dans vos vues ou signaux
2. Appeler la méthode appropriée lors d'événements spécifiques

Exemple d'intégration avec le module de révision de flashcards:

```python
# Dans une vue qui génère des cartes à réviser
def generate_flashcard_revision(user):
    # Logique pour générer des flashcards à réviser
    due_cards = generate_due_cards(user)
    
    # Si des cartes sont à réviser, envoyer une notification
    if due_cards.count() > 0:
        NotificationManager.send_flashcard_reminder(
            user=user,
            due_count=due_cards.count(),
            deck_name="Révision quotidienne"
        )
```

## Configuration & Personnalisation

Vous pouvez personnaliser le comportement du système de notifications en modifiant les modèles et les classes utilitaires selon vos besoins. Les principales options de personnalisation incluent:

- Ajout de nouveaux types de notification dans `NotificationType`
- Modification de la durée d'expiration par défaut des notifications
- Personnalisation de l'apparence des notifications dans l'interface d'administration

## Nettoyage Automatique des Notifications

Les notifications expirent automatiquement en fonction de leur date d'expiration. Si vous souhaitez nettoyer régulièrement les notifications expirées, vous pouvez créer une tâche planifiée:

```python
# Dans une commande Django ou une tâche Celery
def cleanup_expired_notifications():
    from django.utils import timezone
    from apps.notification.models import Notification
    
    # Supprimer les notifications expirées
    deleted, _ = Notification.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()
    
    print(f"Nettoyé {deleted} notifications expirées")
```

## Considérations de Performance

Pour les grands volumes de notifications:

1. Utilisez `send_bulk_notification` au lieu de créer des notifications individuelles
2. Définissez des dates d'expiration appropriées pour toutes les notifications
3. Nettoyez régulièrement les anciennes notifications
4. Considérez l'utilisation d'un broker de message comme Redis ou RabbitMQ pour les WebSockets de notification dans un environnement de production