import React from 'react';
import { Sidebar } from './_components/sidebar';
import UnitList from '../(learning)/courses/course/UnitList';
import UnitsGrid from '../(learning)/courses/course/UnitsGrid';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <div className="h-full flex">
            {/* Sidebar Section */}
            <aside className="hidden md:flex h-full w-56 flex-col fixed inset-y-0 z-50 bg-gray-100 border-r shadow-sm">
                <Sidebar />
            </aside>

            {/* Main Content Section */}
            <div className="flex-1 flex flex-col md:ml-56">
                <main className="flex-1 p-6 overflow-auto">
                    <UnitList />
                    {children}
                </main>

                {/* Section pour afficher les unités */}
                <section className="p-6 bg-white border-t">
                    <UnitsGrid />
                </section>
            </div>
        </div>
    );
}

export default DashboardLayout;
