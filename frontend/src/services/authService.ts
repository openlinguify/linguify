// src/services/authService.ts
import api from './api';

interface LoginResponse {
  token: string;
  user: {
    email: string;
    id: string;
    name: string;
  };
}

interface LoginCredentials {
  email: string;
  password: string;
}

export class AuthService {
  private static readonly TOKEN_KEY = 'auth_token';

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/api/v1/auth/login/', credentials);
      
      if (response.data.token) {
        localStorage.setItem(AuthService.TOKEN_KEY, response.data.token);
      }

      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  logout(): void {
    localStorage.removeItem(AuthService.TOKEN_KEY);
    window.location.href = '/login';
  }

  getAuthToken(): string | null {
    return localStorage.getItem(AuthService.TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }
}

export const authService = new AuthService();
export default authService;