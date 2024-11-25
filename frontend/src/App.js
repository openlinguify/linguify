import React, { Component } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import { Modal, Button, Pagination } from "react-bootstrap";
import CourseCard from "./components/CourseCard";
import HeaderProfile from "./components/Profile/Header/HeaderProfile"; // Import HeaderProfile
import Profile from "./components/Profile/Profile";
import {BrowserRouter as Router, Route, Routes} from "react-router-dom"; // Import Profile



class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      courses: [],
      searchTerm: "",
      filterCategory: "all",
      sortOption: "none",
      currentPage: 1,
      coursesPerPage: 6,
      showModal: false,
      selectedCourse: null,
    };
  }

  componentDidMount() {
    this.fetchCourses();
  }

  fetchCourses = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/courses/");
      this.setState({ courses: response.data });
    } catch (error) {
      console.error("Erreur lors de la récupération des cours !", error);
    }
  };

  handleSearchChange = (event) => {
    this.setState({ searchTerm: event.target.value, currentPage: 1 });
  };

  handleCategoryChange = (event) => {
    this.setState({ filterCategory: event.target.value, currentPage: 1 });
  };

  handleSortChange = (event) => {
    this.setState({ sortOption: event.target.value });
  };

  handlePageChange = (pageNumber) => {
    this.setState({ currentPage: pageNumber });
  };

  handleShowModal = (course) => {
    this.setState({ showModal: true, selectedCourse: course });
  };

  handleCloseModal = () => {
    this.setState({ showModal: false, selectedCourse: null });
  };

  filterCourses = () => {
    const { courses, searchTerm, filterCategory } = this.state;
    return courses.filter((course) => {
      const matchesSearch = course.course_languages_title
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesCategory =
        filterCategory === "all" ||
        (course.category && course.category.category_name === filterCategory);
      return matchesSearch && matchesCategory;
    });
  };

  sortCourses = (courses) => {
    const { sortOption } = this.state;
    if (sortOption === "title") {
      return courses.sort((a, b) =>
        a.course_languages_title.localeCompare(b.course_languages_title)
      );
    } else if (sortOption === "category") {
      return courses.sort((a, b) => {
        if (a.category && b.category) {
          return a.category.category_name.localeCompare(
            b.category.category_name
          );
        }
        return 0;
      });
    }
    return courses;
  };

  renderCourses = () => {
    const { currentPage, coursesPerPage } = this.state;
    const filteredCourses = this.filterCourses();
    const sortedCourses = this.sortCourses(filteredCourses);

    // Pagination
    const indexOfLastCourse = currentPage * coursesPerPage;
    const indexOfFirstCourse = indexOfLastCourse - coursesPerPage;
    const currentCourses = sortedCourses.slice(
      indexOfFirstCourse,
      indexOfLastCourse
    );

    // Utiliser le composant CourseCard
    return currentCourses.map((course) => (
      <CourseCard
        key={course.course_languages_id}
        course={course}
        onClick={this.handleShowModal}
      />
    ));
  };

  renderPagination = () => {
    const { coursesPerPage } = this.state;
    const totalCourses = this.filterCourses().length;
    const pageNumbers = [];

    for (let i = 1; i <= Math.ceil(totalCourses / coursesPerPage); i++) {
      pageNumbers.push(i);
    }

    return (
      <Pagination className="justify-content-center">
        {pageNumbers.map((number) => (
          <Pagination.Item
            key={number}
            active={number === this.state.currentPage}
            onClick={() => this.handlePageChange(number)}
          >
            {number}
          </Pagination.Item>
        ))}
      </Pagination>
    );
  };

  render() {
    const { showModal, selectedCourse } = this.state;
    const username = "Louis-Philippe";
    const profilePicture = "http://localhost:8000/path/to/profile-picture.jpg";

    return (
      <Router>
        <HeaderProfile username={username} profilePicture={profilePicture} />
        <div className="d-flex">
          <div className="bg-light p-4" style={{ width: "250px" }}>
            <h4>Menu</h4>
            <ul className="list-unstyled">
              {/* Ajoutez un lien pour accéder au profil */}
              <li>
                <a href="/profile" className="text-decoration-none">Mon Profil</a>
              </li>
              <li>
                <input
                  type="text"
                  className="form-control mb-3"
                  placeholder="Rechercher un cours..."
                  value={this.state.searchTerm}
                  onChange={this.handleSearchChange}
                />
              </li>
              <li>
                <select
                  className="form-control mb-3"
                  value={this.state.filterCategory}
                  onChange={this.handleCategoryChange}
                >
                  <option value="all">Toutes les catégories</option>
                  {Array.from(
                    new Set(
                      this.state.courses.map(
                        (course) =>
                          course.category && course.category.category_name
                      )
                    )
                  )
                    .filter((category) => category)
                    .map((category) => (
                      <option key={category} value={category}>
                        {category}
                      </option>
                    ))}
                </select>
              </li>
              <li>
                <select
                  className="form-control"
                  value={this.state.sortOption}
                  onChange={this.handleSortChange}
                >
                  <option value="none">Trier par</option>
                  <option value="title">Titre</option>
                  <option value="category">Catégorie</option>
                </select>
              </li>
            </ul>
          </div>

          <main className="container-fluid">
            <Routes>
              <Route
                path="/"
                element={
                  <>
                    <h1 className="text-center my-4">Cours de Langues</h1>
                    <div className="row">{this.renderCourses()}</div>
                    {this.renderPagination()}
                  </>
                }
              />
              <Route path="/profile" element={<Profile />} /> {/* Route pour le profil */}
            </Routes>

            {/* Modale pour les détails du cours */}
            <Modal show={showModal} onHide={this.handleCloseModal}>
              {selectedCourse && (
                <>
                  <Modal.Header closeButton>
                    <Modal.Title>{selectedCourse.course_languages_title}</Modal.Title>
                  </Modal.Header>
                  <Modal.Body>
                    {selectedCourse.course_image && (
                      <img
                        src={`http://localhost:8000${selectedCourse.course_image}`}
                        alt={selectedCourse.course_languages_title}
                        className="img-fluid mb-3"
                      />
                    )}
                    <p>{selectedCourse.course_description}</p>
                    <p>
                      <strong>Catégorie :</strong>{" "}
                      {selectedCourse.category
                        ? selectedCourse.category.category_name
                        : "Non définie"}
                    </p>
                  </Modal.Body>
                  <Modal.Footer>
                    <Button variant="secondary" onClick={this.handleCloseModal}>
                      Fermer
                    </Button>
                    <Button variant="primary">S'inscrire</Button>
                  </Modal.Footer>
                </>
              )}
            </Modal>
          </main>
        </div>
      </Router>
    );
  }
}

export default App;
