// src/services/userAPI.ts
import api from '@/core/api/apiClient';
import { User } from '@/core/types/user';

// Type pour les mises à jour partielles du profil utilisateur
export type PartialUserProfile = Partial<Omit<User, 'id' | 'created_at' | 'updated_at'>>;

// Définition des types pour les paramètres des requêtes
export interface ProfilePictureUploadParams {
  profile_picture: File;
}

/**
 * Service centralisé pour toutes les opérations liées aux utilisateurs
 */
class UserApiService {
  private readonly BASE_URL = '/api/auth';
  
  /**
   * Récupère le profil complet de l'utilisateur actuel depuis le backend
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get(`${this.BASE_URL}/me/`);
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de la récupération du profil utilisateur', error);
      throw error;
    }
  }

  /**
   * Met à jour le profil de l'utilisateur courant
   * @param userData Données partielles du profil à mettre à jour
   */
  async updateUserProfile(userData: PartialUserProfile): Promise<User> {
    try {
      // Utiliser /api/auth/me/ au lieu de /api/auth/user/
      const response = await api.patch(`${this.BASE_URL}/me/`, userData);
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de la mise à jour du profil utilisateur', error);
      throw error;
    }
  }

  /**
   * Upload d'une photo de profil
   * @param file Fichier image à uploader
   */
  async uploadProfilePicture(file: File): Promise<{ profile_picture: string }> {
    try {
      const formData = new FormData();
      formData.append('profile_picture', file);
  
      // Utiliser le bon chemin pour l'upload de photo
      const response = await api.post(`${this.BASE_URL}/me/profile-picture/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de l\'upload de la photo de profil', error);
      throw error;
    }
  }

  /**
   * Récupère les préférences d'apprentissage de l'utilisateur
   */
  async getUserLearningPreferences(): Promise<{
    native_language: string;
    target_language: string;
    language_level: string;
    objectives: string;
  }> {
    try {
      const response = await api.get(`${this.BASE_URL}/user/preferences/`);
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de la récupération des préférences d\'apprentissage', error);
      throw error;
    }
  }

  /**
   * Met à jour les préférences d'apprentissage de l'utilisateur
   */
  async updateLearningPreferences(preferences: {
    native_language?: string;
    target_language?: string;
    language_level?: string;
    objectives?: string;
  }): Promise<{
    native_language: string;
    target_language: string;
    language_level: string;
    objectives: string;
  }> {
    try {
      const response = await api.patch(`${this.BASE_URL}/user/preferences/`, preferences);
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de la mise à jour des préférences d\'apprentissage', error);
      throw error;
    }
  }

  /**
   * Vérifie si l'utilisateur actuel est abonné à un plan premium
   */
  async checkSubscriptionStatus(): Promise<{ is_subscribed: boolean; plan_type?: string; expires_at?: string }> {
    try {
      const response = await api.get(`${this.BASE_URL}/user/subscription/`);
      return response.data;
    } catch (error) {
      this.handleError('Erreur lors de la vérification du statut d\'abonnement', error);
      throw error;
    }
  }

  /**
   * Récupère l'historique d'activité de l'utilisateur
   */
  async getUserActivity(limit: number = 10): Promise<any[]> {
    try {
      const response = await api.get(`${this.BASE_URL}/user/activity/`, {
        params: { limit }
      });
      return response.data.results;
    } catch (error) {
      this.handleError('Erreur lors de la récupération de l\'historique d\'activité', error);
      throw error;
    }
  }

  /**
   * Convertit un objet User partiel aux attributs attendus par le backend Django
   * (utile pour la compatibilité avec différentes conventions de nommage)
   */
  convertToBackendFormat(userData: PartialUserProfile): Record<string, any> {
    // Cette méthode peut être utilisée pour transformer les données si nécessaire
    // Par exemple, convertir camelCase en snake_case si votre API l'attend
    return userData;
  }

  /**
   * Gestion centralisée des erreurs
   */
  private handleError(message: string, error: any): void {
    console.error(`[UserAPI] ${message}:`, {
      error,
      status: error.response?.status,
      data: error.response?.data,
    });
    
    // Ici vous pourriez ajouter d'autres logiques comme:
    // - Envoyer les erreurs à un service de monitoring
    // - Formatter les messages d'erreur pour l'UI
    // - Gérer des cas spécifiques selon les codes d'erreur
  }
}

// Exporter une instance singleton du service
export const userApiService = new UserApiService();

// Exposer également l'ancienne interface userSettingsService pour compatibilité
// Cela permet une migration progressive vers la nouvelle API
export interface UserSettings {
  profile: {
    firstName: string;
    lastName: string;
    email: string;
    bio: string | null;
  };
  language: {
    nativeLanguage: string;
    targetLanguage: string;
    level: string;
  };
  learning: {
    objectives: string;
  };
  account: {
    isCoach: boolean;
    isSubscribed: boolean;
  };
}

export type PartialUserSettings = Partial<UserSettings>;

// Adaptateur de compatibilité pour l'ancienne API
class LegacyUserSettingsAdapter {
  async getUserSettings(): Promise<UserSettings> {
    try {
      const userData = await userApiService.getCurrentUser();
      return this.transformUserToSettings(userData);
    } catch (error) {
      console.error('Error fetching user settings', error);
      throw error;
    }
  }

  async updateUserSettings(settings: PartialUserSettings): Promise<UserSettings> {
    try {
      const payload = this.transformSettingsToUserData(settings);
      const userData = await userApiService.updateUserProfile(payload);
      return this.transformUserToSettings(userData);
    } catch (error) {
      console.error('Error updating user settings', error);
      throw error;
    }
  }

  private transformUserToSettings(userData: User): UserSettings {
    return {
      profile: {
        firstName: userData.first_name || '',
        lastName: userData.last_name || '',
        email: userData.email || '',
        bio: userData.bio,
      },
      language: {
        nativeLanguage: userData.native_language || '',
        targetLanguage: userData.target_language || '',
        level: userData.language_level || '',
      },
      learning: {
        objectives: userData.objectives || '',
      },
      account: {
        isCoach: Boolean(userData.is_coach),
        isSubscribed: Boolean(userData.is_subscribed),
      },
    };
  }

  private transformSettingsToUserData(settings: PartialUserSettings): PartialUserProfile {
    const userData: PartialUserProfile = {};

    if (settings.profile) {
      if (settings.profile.firstName !== undefined) userData.first_name = settings.profile.firstName;
      if (settings.profile.lastName !== undefined) userData.last_name = settings.profile.lastName;
      if (settings.profile.bio !== undefined) userData.bio = settings.profile.bio;
    }

    if (settings.language) {
      if (settings.language.nativeLanguage !== undefined) userData.native_language = settings.language.nativeLanguage as any;
      if (settings.language.targetLanguage !== undefined) userData.target_language = settings.language.targetLanguage as any;
      if (settings.language.level !== undefined) userData.language_level = settings.language.level;
    }

    if (settings.learning?.objectives !== undefined) {
      userData.objectives = settings.learning.objectives;
    }

    return userData;
  }
}

// Exporter l'adaptateur avec le même nom que l'ancien service pour compatibilité
export const userSettingsService = new LegacyUserSettingsAdapter();