// Code: frontend/src/app/(auth)/logout/components/LogoutButton.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';

const LogoutButton = () => {
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      // Appeler l'endpoint de déconnexion du backend
      const response = await axios.post('http://localhost:8000/api/v1/auth/logout');
      
      // Rediriger vers l'URL de déconnexion Auth0
      if (response.data.logoutUrl) {
        window.location.href = response.data.logoutUrl;
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="flex items-center w-full px-3 py-2 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
    >
      <span className="ml-2">
        {isLoading ? 'Logging out...' : 'Log out'}
      </span>
    </button>
  );
};

export default LogoutButton;