// src/components/Themes/Themes.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function Themes() {
  const [themes, setThemes] = useState([]);

  useEffect(() => {
    axios.get('/api/themes/')
      .then(response => setThemes(response.data))
      .catch(error => console.error('Erreur:', error));
  }, []);

  return (
    <div>
      <h1>Thèmes</h1>
      <ul>
        {themes.map(theme => (
          <li key={theme.id}>
            <Link to={`/theme/${theme.id}`}>{theme.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Themes;

