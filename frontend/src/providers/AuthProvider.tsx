"use client";

import { Auth0Provider } from "@auth0/auth0-react";
import { createContext, useContext, ReactNode } from "react";
import useAuthHook, { User } from "@/hooks/useAuth";

// Types pour le contexte d'authentification
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: Error | null;
  token: string | null;
  login: (returnTo?: string) => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
  refreshAuth: () => Promise<boolean>;
}

// Contexte d'authentification
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Composant de contenu du provider
function AuthProviderContent({ children }: { children: ReactNode }) {
  // Utiliser notre hook personnalisé useAuth
  const auth = useAuthHook();
  
  // Fournir le contexte à tous les composants enfants
  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
}

// Provider principal qui initialise Auth0
export function AuthProvider({ children }: { children: ReactNode }) {
  // Configuration de base pour Auth0
  const authConfig = {
    domain: process.env.NEXT_PUBLIC_AUTH0_DOMAIN!,
    clientId: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!,
    authorizationParams: {
      redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/callback`,
      audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
      scope: 'openid profile email'
    },
    useRefreshTokens: true,
    cacheLocation: "localstorage" as const
  };

  return (
    <Auth0Provider {...authConfig}>
      <AuthProviderContent>{children}</AuthProviderContent>
    </Auth0Provider>
  );
}

// Hook pour utiliser le contexte d'authentification
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export default AuthProvider;