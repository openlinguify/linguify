import React from "react";
import { Modal, Button } from "react-bootstrap";

interface Course {
  course_languages_title: string;
  course_image?: string;
  course_description: string;
  category?: { category_name: string };
}

const ModalCourseDetail = ({
  showModal,
  selectedCourse,
  handleClose,
}: {
  showModal: boolean;
  selectedCourse: Course | null;
  handleClose: () => void;
}) => {
  if (!selectedCourse) return null;

  return (
    <Modal show={showModal} onHide={handleClose}>
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
          {selectedCourse.category?.category_name || "Non défini"}
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Fermer
        </Button>
        <Button variant="primary">S'inscrire</Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ModalCourseDetail;
