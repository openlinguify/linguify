import React from "react";

interface Course {
  course_languages_id: number;
  course_languages_title: string;
  course_image?: string;
  category?: { category_name: string };
}

const CourseCard = ({
  course,
  onClick,
}: {
  course: Course;
  onClick: () => void;
}) => {
  return (
    <div className="col-md-4 mb-4" onClick={onClick} style={{ cursor: "pointer" }}>
      <div className="card shadow">
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
            {course.category?.category_name || "Non défini"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;
