// src/app/(auth)/(routes)/layout.tsx
import { Globe } from "lucide-react";
import { AuthCard } from "./_components/auth-card";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      {/* Logo and Brand */}
      <div className="mb-8 flex items-center gap-2">
        <Globe className="h-8 w-8 text-sky-500" />
        <span className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
          Linguify
        </span>
      </div>

      {/* Auth Card Container */}
      <AuthCard>
        {children}
      </AuthCard>

      {/* Footer */}
      <footer className="mt-8 text-center text-sm text-gray-500">
        <p>
          By continuing, you agree to our{" "}
          <a href="/terms" className="text-sky-600 hover:underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="text-sky-600 hover:underline">
            Privacy Policy
          </a>
        </p>
      </footer>
    </div>
  );
}