import React, { Component } from "react";
import axios from "axios";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      courses: [],
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
      console.error("There was an error fetching the courses!", error);
    }
  };

  renderCourses = () => {
    return this.state.courses.map((course) => (
      <div key={course.course_languages_id} className="col-md-4 mb-4">
        <div className="card h-100">
          {course.course_image && (
            <img
              src={`http://localhost:8000${course.course_image}`}
              alt={course.course_languages_title}
              className="card-img-top"
            />
          )}
          <div className="card-body">
            <h5 className="card-title">{course.course_languages_title}</h5>
            <p className="card-text">{course.course_description}</p>
          </div>
          <div className="card-footer">
            <small className="text-muted">
              Catégorie : {course.category ? course.category.category_name : "Non définie"}
            </small>
          </div>
        </div>
      </div>
    ));
  };

  render() {
    return (
      <main className="container">
        <h1 className="text-center my-4">Cours de Langues</h1>
        <div className="row">
          {this.renderCourses()}
        </div>
      </main>
    );
  }
}

export default App;
