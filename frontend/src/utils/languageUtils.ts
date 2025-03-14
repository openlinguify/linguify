// src/utils/languageUtils.ts

/**
 * Récupère la langue cible de l'utilisateur depuis les paramètres stockés
 * Normalise la langue au format attendu par l'API (en, fr, es, nl)
 */
export function getUserTargetLanguage(): string {
  try {
    // Récupérer depuis localStorage
    const userSettingsStr = localStorage.getItem('userSettings');
    if (userSettingsStr) {
      const userSettings = JSON.parse(userSettingsStr);
      if (userSettings.target_language) {
        // Normaliser le format (EN -> en, FR -> fr, etc.)
        const lang = userSettings.target_language.toLowerCase();
        // Vérifier que c'est une langue supportée
        if (['en', 'fr', 'es', 'nl'].includes(lang)) {
          return lang;
        }
      }
    }
  } catch (error) {
    console.error('Error getting user target language:', error);
  }
  
  // Valeur par défaut si aucune langue valide n'est trouvée
  return 'en';
}

/**
 * Configure les en-têtes HTTP appropriés pour les requêtes API
 * avec la langue cible de l'utilisateur
 */
export function getLanguageHeaders(targetLanguage?: string): Headers {
  const headers = new Headers({
    'Content-Type': 'application/json',
  });
  
  // Utiliser la langue spécifiée ou récupérer depuis les paramètres utilisateur
  const lang = targetLanguage || getUserTargetLanguage();
  
  // Ajouter l'en-tête Accept-Language pour les API qui s'appuient sur cet en-tête
  headers.append('Accept-Language', lang);
  
  return headers;
}

/**
 * Ajoute le paramètre de langue cible à une URL d'API
 */
export function addLanguageParam(url: URL, targetLanguage?: string): URL {
  const lang = targetLanguage || getUserTargetLanguage();
  url.searchParams.append('target_language', lang);
  return url;
}