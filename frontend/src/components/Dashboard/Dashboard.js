import React from 'react';
import { ProgressBar, Card } from 'react-bootstrap';

const Dashboard = ({ progress, badges }) => {
  return (
    <div className="container my-5">
      <h2 className="mb-4">Tableau de Bord</h2>

      {/* Progression de l'Apprentissage */}
      <Card className="mb-4 shadow">
        <Card.Body>
          <h5>Progression de l'Apprentissage</h5>
          <ProgressBar now={progress} label={`${progress}%`} />
        </Card.Body>
      </Card>

      {/* Badges et Récompenses */}
      <div className="mb-4">
        <h5>Badges Récompensés</h5>
        <div className="d-flex flex-wrap">
          {badges.length > 0 ? (
            badges.map((badge, index) => (
              <div
                key={index}
                className="badge bg-success text-white me-2 mb-2 p-3 rounded"
              >
                {badge}
              </div>
            ))
          ) : (
            <p>Pas encore de badges gagnés.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
