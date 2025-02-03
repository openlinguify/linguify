// src/hooks/useAuth.ts
import { useUser } from '@auth0/nextjs-auth0/client';

export default function useAuth() {
  const { user, error, isLoading } = useUser();
  
  const getAccessToken = async () => {
    const res = await fetch('/api/auth/token');
    const { accessToken } = await res.json();
    return accessToken;
  };

  return {
    user,
    isLoading,
    error,
    getAccessToken
  };
}