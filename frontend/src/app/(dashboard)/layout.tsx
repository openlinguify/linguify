// frontend/src/app/%28dashboard%29/layout.tsx
import React from 'react';
import { Sidebar } from './_components/sidebar';
import UnitList from '../(course)/(routes)/course/UnitList';
import UnitsGrid from '../(course)/(routes)/course/UnitsGrid';

const DashboardLayout = ({
    children
}: {
    children: React.ReactNode;
}) => {
    return (
        <div className="h-full flex">
            <div className="hidden md:flex h-full w-56 flex-col fixed inset-y-0 z-50">
                <Sidebar />
            </div>

            {/* Main content of the Units */}
            <div className="flex-1 p-6 ml-56">
                <UnitList />
                {children}
            </div>
            <div>
                <UnitsGrid />
                {children}
            </div>
        </div>
    );

}

export default DashboardLayout;
