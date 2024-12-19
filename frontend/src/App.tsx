import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HeaderProfile from "../components/HeaderProfile";
import Sidebar from "../components/Sidebar";
import CourseCard from "../components/CourseCard";
import CourseModal from "../components/CourseModal";
import Profile from "./Profile";
import { Pagination } from "react-bootstrap";
import { getCourses } from "../api";

type Course = {
  course_languages_id: string;
  course_languages_title: string;
  category: { category_name: string };
};

const App: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");
  const [sortOption, setSortOption] = useState("none");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const coursesPerPage = 6;

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const data = await getCourses();
        setCourses(data);
      } catch (err) {
        setError("Failed to fetch courses.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  const filteredCourses = courses.filter((course) =>
    course.course_languages_title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentCourses = filteredCourses.slice(
    (currentPage - 1) * coursesPerPage,
    currentPage * coursesPerPage
  );

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <Router>
      <HeaderProfile
        username="Louis-Philippe"
        profilePicture="http://localhost:8000/path/to/profile-picture.jpg"
      />
      <div className="d-flex">
        <Sidebar
          searchTerm={searchTerm}
          onSearchChange={(e) => setSearchTerm(e.target.value)}
          filterCategory={filterCategory}
          onCategoryChange={(e) => setFilterCategory(e.target.value)}
          sortOption={sortOption}
          onSortChange={(e) => setSortOption(e.target.value)}
          categories={Array.from(
            new Set(courses.map((course) => course.category?.category_name).filter(Boolean))
          )}
        />
        <main className="container-fluid">
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <h1 className="text-center my-4">Cours de Langues</h1>
                  <div className="row">
                    {currentCourses.map((course) => (
                      <CourseCard
                        key={course.course_languages_id}
                        course={course}
                        onClick={() => {
                          setSelectedCourse(course);
                          setShowModal(true);
                        }}
                      />
                    ))}
                  </div>
                  <Pagination>
                    {/* Pagination rendering */}
                  </Pagination>
                </>
              }
            />
            <Route path="/profile" element={<Profile />} />
          </Routes>
          <CourseModal
            show={showModal}
            onClose={() => setShowModal(false)}
            course={selectedCourse}
          />
        </main>
      </div>
    </Router>
  );
};

export default App;
