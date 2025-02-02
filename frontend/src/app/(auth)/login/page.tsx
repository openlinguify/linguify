// src/app/(auth)/(routes)/login/page.tsx
"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useRouter } from "next/navigation";
import React from "react";
import { AuthUI } from "../_components/AuthUI";

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleLogin = async (provider: string) => {
    try {
      setError(null);
      setIsLoading(true);
      await login({
        connection: provider === "github" ? "github" : undefined,
        appState: { returnTo: "/dashboard" },
      });
    } catch (err) {
      setError("An error occurred during login. Please try again.");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthUI 
      mode="login"
      error={error}
      isLoading={isLoading}
      onSubmit={handleLogin}
    />
  );
}