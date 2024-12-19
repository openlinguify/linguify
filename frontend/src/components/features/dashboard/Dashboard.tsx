import React, { useEffect, useState } from "react";
import Sidebar from "../../layout/AdvancedSidebar";
import LearningProgress from "../progress/LearningProgress";
import { fetchCourses } from "../../../services/api/data";
import { fetchUserProfile } from "../../../services/api/user";
import CourseList from "../../../components/features/course/CourseList";
import UserProfileHeader from "../profile/UserProfileHeader";
// Types
interface Course {
  id: number;
  title: string;
  description?: string;
}

interface UserProfile {
  name: string;
  email: string;
}

interface UserProfileHeaderProps {
  userProfile: UserProfile | null;
}

const Dashboard: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [progress, setProgress] = useState<number>(65); // Simulated Progress
  const [badges, setBadges] = useState<string[]>(["Débutant", "Intermédiaire", "Avancé"]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch Data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [coursesData, userProfileData] = await Promise.all([
          fetchCourses(),
          fetchUserProfile(),
        ]);
        setCourses(coursesData);
        setUserProfile(userProfileData);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load data. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return <p className="text-center text-gray-500">Loading...</p>;
  }

  if (error) {
    return (
        <div className="text-center text-danger">
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Retry
          </button>
        </div>
    );
  }

  return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar isExpanded={isExpanded} setIsExpanded={setIsExpanded} />
        <main className={`transition-all duration-300 ${isExpanded ? "ml-64" : "ml-20"}`}>
          <div className="p-8">

            <UserProfileHeader userProfile={userProfile} />
            <LearningProgress progress={progress} badges={badges} />
            <CourseList courses={courses} />


          </div>
        </main>
      </div>
  );
};

export default Dashboard;
