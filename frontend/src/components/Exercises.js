// src/components/Exercises.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

function Exercises() {
  const { unitId } = useParams();
  const [exercises, setExercises] = useState([]);

  useEffect(() => {
    axios.get(`/api/units/${unitId}/exercises/`)
      .then(response => setExercises(response.data))
      .catch(error => console.error('Erreur:', error));
  }, [unitId]);

  return (
    <div>
      <h1>Exercices</h1>
      <ul>
        {exercises.map(exercise => (
          <li key={exercise.id}>{exercise.content}</li>
        ))}
      </ul>
    </div>
  );
}

export default Exercises;
