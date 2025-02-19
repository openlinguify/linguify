// app/login/page.tsx
'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  const handleLogin = async () => {
    try {
      // Obtenir l'URL d'authentification du backend
      const response = await fetch('http://localhost:8000/api/auth/login/');
      const data = await response.json();
      
      if (data.auth_url) {
        // Rediriger vers Auth0
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Welcome to Linguify</h1>
        <Button onClick={handleLogin} className="w-full">
          Login with Auth0
        </Button>
      </div>
    </div>
  );
}