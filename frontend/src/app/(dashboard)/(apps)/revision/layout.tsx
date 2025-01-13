// src/app/(apps)/revision/layout.tsx
export default function RevisionLayout({
    children,
  }: {
    children: React.ReactNode;
  }) {
    return (
      <div className="flex min-h-screen flex-col">
        <div className="flex-1">{children}</div>
      </div>
    );
  }