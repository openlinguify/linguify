import React from "react";

const CourseCard = ({ course, onClick }) => {
  return (
    <div className="col-md-4 mb-4">
      <div
        className="card h-100"
        onClick={() => onClick(course)}
        style={{ cursor: "pointer" }}
      >
        {course.course_image && (
          <img
            src={`http://localhost:8000${course.course_image}`}
            alt={course.course_languages_title}
            className="card-img-top"
          />
        )}
        <div className="card-body">
          <h5 className="card-title">{course.course_languages_title}</h5>
          <p className="card-text">
            {course.course_description.substring(0, 100)}...
          </p>
        </div>
        <div className="card-footer">
          <small className="text-muted">
            Catégorie :{" "}
            {course.category ? course.category.category_name : "Non définie"}
          </small>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;
