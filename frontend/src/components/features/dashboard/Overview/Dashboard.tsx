import React, { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import { fetchCourses } from "../../../../services/api/data";
import { fetchUserProfile } from "../../../../services/api/user";
import LearningProgress from "../../progress/LearningProgress";


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

const Dashboard: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [progress, setProgress] = useState<number>(0);
  const [badges, setBadges] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true); // État de chargement

  // Charger les données
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [coursesData, userProfileData] = await Promise.all([
          fetchCourses(),
          fetchUserProfile(),
        ]);

        // Simuler des données de progression et de badges si non disponibles via API
        const simulatedProgress = 65;
        const simulatedBadges = ["Débutant", "Intermédiaire"];

        setCourses(coursesData);
        setUserProfile(userProfileData);
        setProgress(simulatedProgress);
        setBadges(simulatedBadges);
      } catch (error) {
        console.error("Erreur lors du chargement des données :", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Affichage conditionnel des données
  const renderCourses = () => {
    if (isLoading) {
      return <p className="text-gray-500">Chargement des cours...</p>;
    }

    if (courses.length === 0) {
      return <p className="text-gray-600">Aucun cours trouvé.</p>;
    }

    return (
      <ul className="list-disc pl-5">
        {courses.map((course) => (
          <li key={course.id} className="mb-2">
            {course.title}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isExpanded={isExpanded} setIsExpanded={setIsExpanded} />
      <div className={`transition-all duration-300 ${isExpanded ? "ml-64" : "ml-20"}`}>
        <div className="p-8">
          {/* En-tête */}
          <h1 className="text-2xl font-bold text-gray-900 mb-8">
            Bienvenue, {userProfile?.name || "Utilisateur"}
          </h1>

          {/* Composant pour la progression et les badges */}
          <LearningProgress progress={progress} badges={badges} />

          {/* Liste des cours */}
          <h2 className="text-xl font-semibold mb-4">Mes Cours</h2>
          {renderCourses()}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
