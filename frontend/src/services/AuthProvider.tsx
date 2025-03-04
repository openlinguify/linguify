// src/services/AuthProvider.tsx
"use client";

import { Auth0Provider } from "@auth0/auth0-react";
import { useRouter } from "next/navigation";
import { ReactNode } from "react";
import { createContext, useContext } from "react";
import { useAuth } from "@/services/useAuth";

// Create a context to share auth state
const AuthContext = createContext<ReturnType<typeof useAuth> | null>(null);

// Parent Auth0 Provider
export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';

  // Callback handler for redirects after login
  const onRedirectCallback = (appState: any) => {
    try {
      // Navigate to the intended route or default to dashboard
      router.push(appState?.returnTo || "/");
    } catch (e) {
      console.error("Error in redirect callback:", e);
      router.push("/");
    }
  };

  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN as string}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID as string}
      authorizationParams={{
        redirect_uri: `${frontendUrl}/callback`,
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE as string,
      }}
      cacheLocation="localstorage"
      useRefreshTokens={true}
      onRedirectCallback={onRedirectCallback}
    >
      <AuthProviderContent>{children}</AuthProviderContent>
    </Auth0Provider>
  );
}

// Inner provider that uses the hook and provides context
function AuthProviderContent({ children }: { children: ReactNode }) {
  const auth = useAuth();
  
  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook to use auth context
export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}