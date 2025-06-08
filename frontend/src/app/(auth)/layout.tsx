// src/app/(auth)/(routes)/layout.tsx

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 min-h-screen flex flex-col items-center justify-center p-6">
      <div className="mb-8 flex items-center gap-2">
        <span className="text-3xl font-bold text-white">
          Open Linguify
        </span>
      </div>

      {/* Main Content */}
      <div>
        {children}
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-white text-sm">
        <p>
          By continuing, you agree to our{" "}
          <a href="/terms" className="text-brand-purple hover:underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="text-brand-purple hover:underline">
            Privacy Policy
          </a>
        </p>
      </footer>
    </div>
  );
}