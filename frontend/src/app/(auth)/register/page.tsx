// src/app/(auth)/(routes)/register/page.tsx
"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useRouter } from "next/navigation";
import React from "react";
import { AuthUI } from "../_components/AuthUI";

export default function RegisterPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleSignup = async (provider: string) => {
    try {
      setError(null);
      setIsLoading(true);
      await login({
        connection: provider === "github" ? "github" : undefined,
        appState: { returnTo: "/onboarding" },
        screen_hint: "signup",
      });
    } catch (err) {
      setError("An error occurred during registration. Please try again.");
      console.error("Registration error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthUI 
      mode="register"
      error={error}
      isLoading={isLoading}
      onSubmit={handleSignup}
    />
  );
}
