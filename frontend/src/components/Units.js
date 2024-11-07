// src/components/Units.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

function Units() {
  const { themeId } = useParams();
  const [units, setUnits] = useState([]);

  useEffect(() => {
    axios.get(`/api/themes/${themeId}/units/`)
      .then(response => setUnits(response.data))
      .catch(error => console.error('Erreur:', error));
  }, [themeId]);

  return (
    <div>
      <h1>Unités</h1>
      <ul>
        {units.map(unit => (
          <li key={unit.id}>
            <Link to={`/unit/${unit.id}`}>{unit.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Units;

