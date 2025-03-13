// src/utils/languageUtils.ts

/**
 * Normalise le code de langue pour l'API
 * 
 * Convertit un code de langue (en majuscules ou minuscules)
 * en format approprié pour les requêtes API
 * 
 * @param code Code de langue à normaliser (ex: 'EN', 'fr', 'NL')
 * @returns Code normalisé en minuscules ('en', 'fr', 'nl')
 */
export function normalizeLanguageCode(code: string | undefined): string {
    if (!code) return 'en';
    
    // Convertir en minuscules
    const lowercaseCode = code.toLowerCase();
    
    // Valider si c'est une langue supportée
    const supportedLanguages = ['en', 'fr', 'es', 'nl'];
    return supportedLanguages.includes(lowercaseCode) ? lowercaseCode : 'en';
  }
  
  /**
   * Récupère la langue cible depuis les paramètres utilisateur
   * stockés dans localStorage
   * 
   * @returns Code de langue normalisé
   */
  export function getUserTargetLanguage(): string {
    try {
      const userSettingsStr = localStorage.getItem('userSettings');
      if (userSettingsStr) {
        const userSettings = JSON.parse(userSettingsStr);
        if (userSettings.target_language) {
          // Normaliser la langue avant de la retourner
          return normalizeLanguageCode(userSettings.target_language);
        }
      }
    } catch (error) {
      console.error('Error retrieving target language from localStorage:', error);
    }
    
    return 'en'; // langue par défaut
  }