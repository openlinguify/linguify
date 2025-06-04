// src/core/api/appManagerApi.ts
import { apiClient } from './apiClient';

export interface App {
  id: number;
  code: string;
  display_name: string;
  description: string;
  icon_name: string;
  color: string;
  route_path: string;
  is_enabled: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface UserAppSettings {
  id: number;
  user: number;
  enabled_apps: App[];
  enabled_app_codes?: string[];
  created_at: string;
  updated_at: string;
}

export interface AppToggleRequest {
  app_code: string;
  enabled: boolean;
}

export interface AppToggleResponse {
  success: boolean;
  message: string;
  enabled_apps: string[];
}

export interface UserEnabledAppsResponse {
  enabled_apps: App[];
  enabled_app_codes: string[];
}

class AppManagerService {
  private baseUrl = '/api/v1/app-manager';

  /**
   * Get all available applications
   */
  async getAvailableApps(): Promise<App[]> {
    const response = await apiClient.get<App[]>(`${this.baseUrl}/apps/`);
    return response.data;
  }

  /**
   * Get user's app settings
   */
  async getUserAppSettings(): Promise<UserAppSettings> {
    const response = await apiClient.get<UserAppSettings>(`${this.baseUrl}/settings/`);
    return response.data;
  }

  /**
   * Update user's app settings
   */
  async updateUserAppSettings(enabledAppCodes: string[]): Promise<UserAppSettings> {
    const response = await apiClient.put<UserAppSettings>(`${this.baseUrl}/settings/`, {
      enabled_app_codes: enabledAppCodes
    });
    return response.data;
  }

  /**
   * Get user's enabled apps
   */
  async getUserEnabledApps(): Promise<UserEnabledAppsResponse> {
    const response = await apiClient.get<UserEnabledAppsResponse>(`${this.baseUrl}/enabled/`);
    return response.data;
  }

  /**
   * Toggle an app on/off for the current user
   */
  async toggleApp(appCode: string, enabled: boolean): Promise<AppToggleResponse> {
    const response = await apiClient.post<AppToggleResponse>(`${this.baseUrl}/toggle/`, {
      app_code: appCode,
      enabled: enabled
    });
    return response.data;
  }

  /**
   * Enable an app for the current user
   */
  async enableApp(appCode: string): Promise<AppToggleResponse> {
    return this.toggleApp(appCode, true);
  }

  /**
   * Disable an app for the current user
   */
  async disableApp(appCode: string): Promise<AppToggleResponse> {
    return this.toggleApp(appCode, false);
  }

  /**
   * Check if an app is enabled for the current user
   */
  async isAppEnabled(appCode: string): Promise<boolean> {
    try {
      const enabledApps = await this.getUserEnabledApps();
      return enabledApps.enabled_app_codes.includes(appCode);
    } catch (error) {
      console.error('Error checking app status:', error);
      return false;
    }
  }
}

// Export singleton instance
export const appManagerService = new AppManagerService();
export default appManagerService;