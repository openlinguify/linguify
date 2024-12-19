import React, { useState, useEffect } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import HeaderProfile from "./components/features/profile/UserProfileHeader";
import Sidebar from "./components/layout/AdvancedSidebar";
import MainContent from "./components/layout/MainContent";
import { fetchUserProfile } from "./services/api/user";

// Types
interface UserProfile {
    name: string;
    email: string;
}

const App: React.FC = () => {
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
    const [isExpanded, setIsExpanded] = useState<boolean>(true);

    // Fetch user profile
    useEffect(() => {
        const fetchData = async () => {
            try {
                const userData = await fetchUserProfile();
                setUserProfile(userData);
            } catch (error) {
                console.error("Error fetching user profile:", error);
            }
        };

        fetchData();
    }, []);

    return (
        <Router>
            <HeaderProfile userProfile={userProfile} />
            <div className="d-flex">
                <Sidebar isExpanded={isExpanded} setIsExpanded={setIsExpanded} />
                <MainContent />
            </div>
        </Router>
    );
};

export default App;
