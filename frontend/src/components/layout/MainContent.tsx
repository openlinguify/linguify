// frontend/src/components/layout/MainContent.tsx
import React, { useState, useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "../features/dashboard/Dashboard";
import UserProfile from "../features/profile/UserProfileHeader";
import Courses from "../features/course/CourseList";
import { fetchUserProfile } from "../../services/api/user";
import { fetchCourses } from "../../services/api/data";
import Themes from "../features/course/Themes";

// Types
type Course = {
    id: number;
    title: string;
    description?: string;
};

type UserProfileData = {
    name: string;
    email: string;
};

const MainContent: React.FC = () => {
    const [userProfile, setUserProfile] = useState<UserProfileData | null>(null);
    const [courses, setCourses] = useState<Course[]>([]);

    useEffect(() => {
        // Fetch user profile
        const fetchData = async () => {
            try {
                const [userData, courseData] = await Promise.all([fetchUserProfile(), fetchCourses()]);
                setUserProfile(userData);
                setCourses(courseData);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, []);

    return (
        <main className="p-4">
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/profile" element={<UserProfile userProfile={userProfile} />} />
                <Route path="/courses" element={<Courses courses={courses} />} />
                <Route path="/Themes" element={<Themes />} />
            </Routes>
        </main>
    );
};

export default MainContent;
