'use client';

import { useEffect, useState } from "react";
import { useSupabaseAuth } from "@/core/auth/SupabaseAuthProvider";
import { useRouter } from "next/navigation";
import { SupabaseLoginForm } from "@/components/auth/SupabaseLoginForm";

export default function LoginPage() {
  const { user, loading } = useSupabaseAuth();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  // Assure que le rendu est côté client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Rediriger l'utilisateur connecté vers le tableau de bord
  useEffect(() => {
    if (isClient && user && !loading) {
      console.log("[Auth Flow] User already authenticated, redirecting to dashboard");
      router.push('/');
    }
  }, [isClient, user, loading, router]);

  // Affiche le formulaire de connexion si l'utilisateur n'est pas connecté
  return (
    <div>
      <SupabaseLoginForm />
    </div>
  );
}
