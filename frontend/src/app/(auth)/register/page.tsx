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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <SupabaseSignUpForm />
    </div>
  );
}