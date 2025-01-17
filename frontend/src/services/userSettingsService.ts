// src/services/userSettingsService.ts
import api from '@/services/api';

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

class UserSettingsService {
  private readonly BASE_URL = '/api/v1/auth/users/profile/';

  async getUserSettings(): Promise<UserSettings> {
    try {
      const response = await api.get(this.BASE_URL);
      return this.transformResponseToSettings(response.data);
    } catch (error) {
      this.handleError('Error fetching user settings', error);
      throw error;
    }
  }

  async updateUserSettings(settings: PartialUserSettings): Promise<UserSettings> {
    try {
      const payload = this.transformSettingsToPayload(settings);
      const response = await api.patch(this.BASE_URL, payload);
      return this.transformResponseToSettings(response.data);
    } catch (error) {
      this.handleError('Error updating user settings', error);
      throw error;
    }
  }

  private transformResponseToSettings(data: any): UserSettings {
    return {
      profile: {
        firstName: data.first_name || '',
        lastName: data.last_name || '',
        email: data.email || '',
        bio: data.bio,
      },
      language: {
        nativeLanguage: data.native_language || '',
        targetLanguage: data.target_language || '',
        level: data.language_level || '',
      },
      learning: {
        objectives: data.objectives || '',
      },
      account: {
        isCoach: Boolean(data.is_coach),
        isSubscribed: Boolean(data.is_subscribed),
      },
    };
  }

  private transformSettingsToPayload(settings: PartialUserSettings): Record<string, any> {
    const payload: Record<string, any> = {};

    if (settings.profile) {
      const { firstName, lastName, bio } = settings.profile;
      if (firstName !== undefined) payload.first_name = firstName;
      if (lastName !== undefined) payload.last_name = lastName;
      if (bio !== undefined) payload.bio = bio;
    }

    if (settings.language) {
      const { nativeLanguage, targetLanguage, level } = settings.language;
      if (nativeLanguage !== undefined) payload.native_language = nativeLanguage;
      if (targetLanguage !== undefined) payload.target_language = targetLanguage;
      if (level !== undefined) payload.language_level = level;
    }

    if (settings.learning?.objectives !== undefined) {
      payload.objectives = settings.learning.objectives;
    }

    return payload;
  }

  private handleError(message: string, error: any): void {
    console.error(message, {
      error,
      status: error.response?.status,
      data: error.response?.data,
    });
  }
}

export const userSettingsService = new UserSettingsService();