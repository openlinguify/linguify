'use client';

import { useEffect, useState } from "react";
import { useSupabaseAuth } from "@/core/auth/SupabaseAuthProvider";
import { useRouter } from "next/navigation";
import { SupabaseLoginForm } from "@/components/auth/SupabaseLoginForm";

export default function LoginPage() {
  const { user, loading } = useSupabaseAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  // Attendre le montage du composant
  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (mounted && user && !loading) {
      console.log("[Auth Flow] User already authenticated, redirecting to dashboard");
      router.push('/');
    }
  }, [mounted, user, loading, router]);

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
      </div>
    );
  }

  // Afficher le formulaire de connexion
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <SupabaseLoginForm />
    </div>
  );
}