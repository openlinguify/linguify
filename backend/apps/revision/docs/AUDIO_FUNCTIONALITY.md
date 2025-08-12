# 🎵 Fonctionnalité Audio des Flashcards - Linguify

## Vue d'ensemble

La fonctionnalité audio permet aux utilisateurs d'entendre les flashcards prononcées avec des voix configurables, améliorant ainsi l'apprentissage des langues par la prononciation correcte.

## ✅ Fonctionnalités Implémentées

### 1. **Paramètres Audio Utilisateur**
- ✅ Configuration des voix préférées par langue (FR, EN, ES, IT, DE)
- ✅ Vitesse de lecture ajustable (0.5x à 2.0x)
- ✅ Activation/désactivation de la synthèse vocale
- ✅ Sauvegarde persistante en base de données

### 2. **Interface des Paramètres**
- ✅ Section "Paramètres audio et voix" dans les settings
- ✅ Sélecteurs de voix par langue avec aperçu
- ✅ Bouton "🎵 Tester" pour chaque voix
- ✅ Sauvegarde automatique des préférences

### 3. **Flashcards avec Audio**
- ✅ Boutons audio sur le recto et verso des flashcards
- ✅ Détection de langue automatique ou explicite
- ✅ Utilisation des voix préférées configurées
- ✅ Animation des boutons pendant la lecture

### 4. **Configuration des Langues**
- ✅ Langues par défaut configurables par deck
- ✅ Attribution des langues au recto/verso
- ✅ Bouton "Appliquer à toutes les cartes" 
- ✅ Normalisation des codes de langue (fr → fr-FR)

## 🏗️ Architecture Technique

### Base de Données
```sql
-- Table: revision_revisionsettings
ALTER TABLE revision_revisionsettings ADD COLUMN audio_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE revision_revisionsettings ADD COLUMN audio_speed FLOAT DEFAULT 0.9;
ALTER TABLE revision_revisionsettings ADD COLUMN preferred_voice_french VARCHAR(200) DEFAULT '';
ALTER TABLE revision_revisionsettings ADD COLUMN preferred_voice_english VARCHAR(200) DEFAULT '';
ALTER TABLE revision_revisionsettings ADD COLUMN preferred_voice_spanish VARCHAR(200) DEFAULT '';
ALTER TABLE revision_revisionsettings ADD COLUMN preferred_voice_italian VARCHAR(200) DEFAULT '';
ALTER TABLE revision_revisionsettings ADD COLUMN preferred_voice_german VARCHAR(200) DEFAULT '';
```

### Modèles Django
```python
# apps/revision/models/settings_models.py
class RevisionSettings(models.Model):
    audio_enabled = models.BooleanField(default=True)
    audio_speed = models.FloatField(default=0.9)
    preferred_voice_french = models.CharField(max_length=200, blank=True)
    preferred_voice_english = models.CharField(max_length=200, blank=True)
    # ... autres langues
```

### API Endpoints
```python
# apps/revision/urls.py
path('user-settings/', get_user_revision_settings, name='user-settings')

# apps/revision/views/revision_settings_views.py
def get_user_revision_settings(request):
    # Retourne les paramètres audio + session de l'utilisateur
```

### JavaScript (Frontend)
```javascript
// apps/revision/static/revision/js/revision-flashcards.js
class FlashcardStudyMode {
    loadUserAudioSettings() {
        // Charge les paramètres depuis window.userAudioSettings (serveur)
        // Fallback vers l'API si non disponible
    }
    
    speakText(side) {
        // Utilise les voix préférées pour synthèse vocale
        // Gère normalisation des langues (fr → fr-FR)
    }
}
```

## 🔄 Flux de Fonctionnement

### 1. Configuration Initiale
```
Utilisateur → Page Paramètres → Section Audio → Sélection Voix → Sauvegarde DB
```

### 2. Utilisation dans les Flashcards  
```
Chargement Page → Récupération Paramètres → Configuration Deck → Mode Flashcards → Clic Audio → Synthèse Vocale
```

### 3. Transmission des Paramètres
```
Django View → Context Template → window.userAudioSettings → JavaScript FlashcardStudyMode
```

## 🧪 Tests Implémentés

### Tests Unitaires
- **AudioSettingsTest**: Création, sauvegarde, récupération des paramètres
- **FlashcardsAudioAPITest**: Tests API et sérialisation
- **FlashcardsLanguageIntegrationTest**: Tests d'intégration complets
- **VoiceMatchingTest**: Correspondance noms de voix

### Tests Couverts
✅ Création des paramètres audio  
✅ Sauvegarde des voix préférées  
✅ Attribution des langues aux flashcards  
✅ API user-settings  
✅ Contexte template avec paramètres audio  
✅ Logique de sélection de voix  
✅ Normalisation des codes de langue  

## 🎯 Exemples d'Usage

### Configuration des Voix
```python
# Paramètres typiques
settings = RevisionSettings.objects.get(user=user)
settings.preferred_voice_french = 'Microsoft Paul - French (France)'  # Masculin
settings.preferred_voice_english = 'Google UK English Male'           # Masculin  
settings.audio_speed = 0.9
settings.save()
```

### Flashcard avec Langues
```python
flashcard = Flashcard.objects.create(
    user=user,
    deck=deck,
    front_text='Hello',          # Texte recto
    back_text='Bonjour',         # Texte verso  
    front_language='en',         # Langue recto
    back_language='fr'           # Langue verso
)
```

### Sélection de Voix (JavaScript)
```javascript
// Logique de sélection dans revision-flashcards.js
const languageToUse = this.normalizeLanguageCode(cardLanguage); // 'en' → 'en-US'
const voice = this.getBestVoiceForLanguage(languageToUse);      // Trouve voix préférée
utterance.voice = voice; // Applique la voix à la synthèse
```

## 🐛 Problèmes Résolus

### 1. **Migration Django**
- **Problème**: Inconsistance migrations 0014/0015
- **Solution**: Migration 0015 marquée comme fake, 0016 créée pour audio
- **Statut**: ✅ Résolu en dev et production

### 2. **API non-fonctionnelle**  
- **Problème**: `get_user_revision_settings` retournait 302 (auth)
- **Solution**: Paramètres passés via contexte template → `window.userAudioSettings`
- **Statut**: ✅ Résolu

### 3. **Voix non trouvées**
- **Problème**: Noms de voix interface ≠ noms réels speechSynthesis
- **Solution**: Utilisation des noms exacts des voix disponibles
- **Statut**: ✅ Résolu

### 4. **Colonnes manquantes**
- **Problème**: Colonnes audio_* absentes en développement
- **Solution**: Ajout manuel + marquage migrations
- **Statut**: ✅ Résolu

## 📋 Checklist de Validation

### Paramètres Audio
- [x] Section visible dans interface settings
- [x] Sélection voix par langue fonctionne
- [x] Boutons test fonctionnent
- [x] Sauvegarde persistante
- [x] Chargement au redémarrage

### Flashcards Audio  
- [x] Boutons audio visibles sur recto/verso
- [x] Clic déclenche synthèse vocale
- [x] Voix configurées utilisées
- [x] Animation pendant lecture
- [x] Gestion des erreurs

### Configuration Langues
- [x] Sélecteurs langue deck fonctionnels
- [x] Application à toutes les cartes
- [x] Langues sauvegardées par flashcard
- [x] Détection automatique si langue vide

### Tests et Qualité
- [x] Tests unitaires passent
- [x] Tests d'intégration couvrent workflow complet
- [x] Documentation à jour
- [x] Code reviewé et optimisé

## 🚀 Utilisation

1. **Configurer les voix**: Paramètres → Révision → Audio et voix
2. **Créer un deck**: Définir langues par défaut recto/verso  
3. **Ajouter flashcards**: Les langues sont appliquées automatiquement
4. **Mode flashcards**: Cliquer boutons 🎵 pour entendre les voix configurées

---

**Statut**: ✅ **Fonctionnel et Testé**  
**Dernière mise à jour**: 10 août 2025  
**Développeur**: Assistant Claude + Louis