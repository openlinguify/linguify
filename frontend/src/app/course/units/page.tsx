"use client"; // Pour que le code soit exécuté côté client et non côté serveur

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
        setUnits((response.data as { results: Unit[] }).results || []);

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
    return <div className="text-center mt-5 text-lg">Chargement en cours...</div>;
  }

  // Affichage des erreurs
  if (error) {
    return <div className="text-center mt-5 text-red-500 text-lg">{error}</div>;
  }

  // Affichage des unités
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6">
      {units.map(unit => (
        <div
          key={unit.id}
          className="p-4 border rounded-lg text-center shadow-md bg-gray-50 hover:scale-105 hover:shadow-lg transition-transform cursor-pointer"
          onClick={() => router.push(`/units/${unit.id}`)}
        >
          <h3 className="font-bold text-lg mb-2">{unit.title}</h3>
          <p className="text-sm mb-2">{unit.description}</p>
          <p className="text-sm font-medium">Niveau : {unit.level}</p>
          <p className="text-sm font-medium">Ordre : {unit.order}</p>
        </div>
      ))}
    </div>
  );
};

export default UnitsGrid;
