// frontend/src/app/(dashboard)/settings/page.tsx
"use client";

import SettingsForm from "./_components/settings-form";

export default function SettingsPage() {
    return (
        <div className="min-h-screen bg-gray-50">
            <SettingsForm />
        </div>
    );
}