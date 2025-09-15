# Tests de Notification

Ce répertoire contient les scripts de test pour le système de notifications d'Open Linguify.

## Scripts disponibles

### 1. `test_all_languages.py`
Envoie les emails de conditions d'utilisation dans toutes les langues supportées.

**Usage:**
```bash
poetry run python apps/notification/tests/test_all_languages.py
```

**Langues supportées:**
- 🇬🇧 English (en)
- 🇫🇷 Français (fr)
- 🇳🇱 Nederlands (nl)
- 🇪🇸 Español (es)

### 2. `test_email_layout.py`
Test rapide du layout email avec le design Linguify.

**Usage:**
```bash
poetry run python apps/notification/tests/test_email_layout.py
```

### 3. `test_multilingual_emails.py`
Test détaillé des emails multilingues avec changement de langue utilisateur.

**Usage:**
```bash
poetry run python apps/notification/tests/test_multilingual_emails.py
```

### 4. `test_multilingual_notifications.py`
Test des notifications dans différentes langues avec création de notifications.

**Usage:**
```bash
poetry run python apps/notification/tests/test_multilingual_notifications.py
```

### 5. `test_terms_email.py`
Test simple d'envoi d'email de conditions d'utilisation.

**Usage:**
```bash
poetry run python apps/notification/tests/test_terms_email.py
```

## Design Email

Les emails utilisent le design Linguify avec :

- **Header** : Gradient `#2D5BBA → #017E84`
- **Logo** : Badge "Open Linguify" blanc sur fond gradient
- **Bouton CTA** : Gradient avec fallback solide pour Outlook
- **Layout** : Table-based pour compatibilité maximale

## Compatibilité

Les templates email sont testés et compatibles avec :
- ✅ Gmail
- ✅ Outlook (toutes versions)
- ✅ Apple Mail
- ✅ Thunderbird
- ✅ Clients mobiles

## Configuration

Les emails de test sont envoyés à : `linguify.info@gmail.com`

L'utilisateur de test est : `louisphilippelalou@outlook.com`

## Traductions

Le système utilise Django i18n avec :
- Templates de base en anglais
- Fichiers `.po` dans `/apps/notification/locale/`
- Activation automatique selon `user.interface_language`

Pour compiler les traductions :
```bash
poetry run python manage.py compilemessages
```