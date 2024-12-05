import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HeaderProfile from "../components/HeaderProfile";
import Sidebar from "../components/Sidebar";
import CourseCard from "../components/CourseCard";
import CourseModal from "../components/CourseModal";
import Profile from "./Profile";
import axios from "axios";
import { Pagination } from "react-bootstrap";

const App: React.FC = () => {
  const [courses, setCourses] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");
  const [sortOption, setSortOption] = useState("none");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const coursesPerPage = 6;

  useEffect(() => {
    const fetchCourses = async () => {
      const { data } = await axios.get("http://localhost:8000/api/courses/");
      setCourses(data);
    };

    fetchCourses();
  }, []);

  const categories = Array.from(
    new Set(courses.map((course) => course.category?.category_name).filter(Boolean))
  );

  const filteredCourses = courses.filter((course) =>
    course.course_languages_title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentCourses = filteredCourses.slice(
    (currentPage - 1) * coursesPerPage,
    currentPage * coursesPerPage
  );

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
          categories={categories}
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
