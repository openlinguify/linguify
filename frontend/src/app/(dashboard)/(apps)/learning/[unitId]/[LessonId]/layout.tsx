// src/app/(dashboard)/(apps)/learning/[unitId]/[lessonId]/layout.tsx
export default function LessonLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div className="h-full min-h-screen bg-background">{children}</div>;
}