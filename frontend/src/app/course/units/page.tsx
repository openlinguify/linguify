"use client"; // Marque ce fichier comme Client Component

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

// Définir le type de données pour une unité
type Unit = {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
};

// Composant principal
const UnitsGrid: React.FC = () => {
  // États
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Récupérer les données de l'API
  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/course/units/');
        // Vérifie que la réponse contient bien des résultats paginés
        setUnits(response.data.results || []);
      } catch (err) {
        console.error("Erreur lors de la récupération des unités :", err);
        setError("Impossible de charger les unités. Veuillez réessayer.");
      } finally {
        setLoading(false); // Arrête le chargement, même en cas d'erreur
      }
    };
    fetchUnits();
  }, []); // Appelé une seule fois au montage

  // Affichage du chargement
  if (loading) {
    return <div style={styles.loading}>Chargement en cours...</div>;
  }

  // Affichage des erreurs
  if (error) {
    return <div style={styles.error}>{error}</div>;
  }

  // Affichage des unités
  return (
    <div style={styles.gridContainer}>
      {units.map(unit => (
        <div
          key={unit.id}
          style={styles.gridItem}
          onClick={() => router.push(`/units/${unit.id}`)}
        >
          <h3 style={styles.title}>{unit.title}</h3>
          <p style={styles.description}>{unit.description}</p>
          <p>Niveau : {unit.level}</p>
          <p>Ordre : {unit.order}</p>
        </div>
      ))}
    </div>
  );
};

// Styles CSS en JS
const styles = {
  gridContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '20px',
    padding: '20px',
  } as React.CSSProperties,

  gridItem: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    textAlign: 'center',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
    backgroundColor: '#f9f9f9',
    '&:hover': {
      transform: 'scale(1.05)',
      boxShadow: '0 6px 12px rgba(0, 0, 0, 0.15)',
    },
  } as React.CSSProperties,

  loading: {
    textAlign: 'center',
    marginTop: '20px',
    fontSize: '18px',
  } as React.CSSProperties,

  error: {
    textAlign: 'center',
    marginTop: '20px',
    color: 'red',
    fontSize: '18px',
  } as React.CSSProperties,

  title: {
    fontWeight: 'bold',
  } as React.CSSProperties,

  description: {
    fontSize: '14px',
    margin: '10px 0',
  } as React.CSSProperties,
};

export default UnitsGrid;
