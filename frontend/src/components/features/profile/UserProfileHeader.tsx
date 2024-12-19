// frontend/src/components/features/profile/UserProfileHeader.tsx
import React from "react";

// Props Type
type UserProfileHeaderProps = {
    userProfile: { name: string; email: string } | null;
};

const UserProfileHeader: React.FC<UserProfileHeaderProps> = ({ userProfile }) => {
    return (
        <header>
            <h1 className="text-2xl font-bold text-gray-900">
                Welcome, {userProfile?.name || "User"}
            </h1>
            <p className="text-gray-600">{userProfile?.email || "No email available"}</p>
        </header>
    );
};

export default UserProfileHeader;
export type { UserProfileHeaderProps };
