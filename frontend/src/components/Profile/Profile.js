import React from 'react';
import { Form, Button } from 'react-bootstrap';

const Profile = ({ user, updateUser }) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    // Logique pour mettre à jour les informations de l'utilisateur
    updateUser();
  };

  return (
    <div className="container my-5">
      <h2 className="mb-4">Profil Utilisateur</h2>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="formUsername">
          <Form.Label>Nom d'utilisateur</Form.Label>
          <Form.Control type="text" defaultValue={user.username} />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formEmail">
          <Form.Label>Email</Form.Label>
          <Form.Control type="email" defaultValue={user.email} />
        </Form.Group>

        <Form.Group className="mb-3" controlId="formBio">
          <Form.Label>Biographie</Form.Label>
          <Form.Control as="textarea" rows={3} defaultValue={user.bio} />
        </Form.Group>

        <Button variant="primary" type="submit">
          Mettre à jour
        </Button>
      </Form>
    </div>
  );
};

export default Profile;
