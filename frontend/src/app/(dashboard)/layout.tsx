import React, { Suspense } from 'react';
import { Sidebar } from './_components/sidebar';

// Loading fallback components
const LoadingUnits = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-8 bg-gray-200 rounded w-1/4"></div>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-48 bg-gray-200 rounded"></div>
      ))}
    </div>
  </div>
);

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-full flex">
      {/* Sidebar Section */}
      <aside className="hidden md:flex h-full w-56 flex-col fixed inset-y-0 z-50 bg-gray-100 border-r shadow-sm">
        <Sidebar />
      </aside>

      {/* Main Content Section */}
      <div className="flex-1 flex flex-col md:ml-56">
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>

        {/* Units Section */}
        <section className="p-6 bg-white border-t">
          <Suspense fallback={<LoadingUnits />}>
            <UnitsList />
          </Suspense>
        </section>
      </div>
    </div>
  );
}

// Import units list component asynchronously
async function UnitsList() {
  const UnitsGrid = (await import('../(apps)/learning/courses/UnitsGrid')).default;
  return <UnitsGrid />;
}