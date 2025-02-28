"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useRouter } from "next/navigation";
import React from "react";
import { Loader2 } from "lucide-react";

export default function LogoutPage() {
  const { logout } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = React.useState(true);

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      
      // Spécifier explicitement l'URL de retour
      await logout({ 
        returnTo: `${window.location.origin}/home` 
      });
      
      // Redirection de secours avec un délai
      // (au cas où la redirection Auth0 ne fonctionnerait pas)
      setTimeout(() => {
        window.location.href = '/home';
      }, 3000);
    } catch (error) {
      console.error("Logout error:", error);
      // En cas d'erreur, rediriger manuellement
      window.location.href = '/home';
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    handleLogout();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <h2 className="text-xl font-semibold mb-2">
          {isLoading ? "Déconnexion en cours..." : "Déconnecté"}
        </h2>
        <p className="text-gray-600">
          Veuillez patienter pendant que nous vous déconnectons en toute sécurité.
        </p>
      </div>
    </div>
  );
}