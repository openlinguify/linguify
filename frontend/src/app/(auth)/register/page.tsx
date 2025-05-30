'use client';

import { useEffect, useState } from "react";
import { useSupabaseAuth } from "@/core/auth/SupabaseAuthProvider";
import { useRouter } from "next/navigation";
import { SupabaseSignUpForm } from "@/components/auth/SupabaseSignUpForm";

export default function RegisterPage() {
  const { user, loading } = useSupabaseAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  // Attendre le montage du composant
  useEffect(() => {
    setMounted(true);
  }, []);

  // Rediriger si déjà authentifié
  useEffect(() => {
    if (mounted && !loading && user) {
      console.log("[Auth Flow] User already authenticated, redirecting to home");
      router.push('/');
    }
  }, [mounted, loading, user, router]);

  // Afficher le spinner pendant le chargement
  if (!mounted || loading) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white">
        {/* Spinner personnalisé */}
        <div className="relative w-16 h-16">
          <div className="absolute top-0 left-0 w-full h-full rounded-full border-4 border-transparent border-t-purple-600 border-r-indigo-500 animate-spin"></div>
          <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
            <div className="w-8 h-8 text-indigo-600 text-xl font-bold">L</div>
          </div>
        </div>
        <p className="mt-4 text-lg text-gray-700 font-medium bg-gradient-to-r from-purple-600 to-indigo-500 bg-clip-text text-transparent">
          Préparation de votre inscription...
        </p>
      </div>
    );
  }

  // Afficher le formulaire d'inscription
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <SupabaseSignUpForm />
    </div>
  );
}