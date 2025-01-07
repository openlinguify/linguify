// frontend/src/app/course/routes/course/UnitList.tsx
"use client";
import React, { useEffect, useState } from 'react';
import { fetchUnits } from '@services/api';


// Interface for Unit
interface Unit {
    id: number;
    title: string;
    description: string;
    level: string;
    order: number;
}

// React Functional Component
const UnitList: React.FC = () => {
    const [units, setUnits] = useState<Unit[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getUnits = async () => {
            try {
                const response = await fetchUnits() as { data: Unit[] }; // Fetch data
                setUnits(response.data); // Update state with units
            } catch (err) {
                setError('Failed to load units'); // Handle errors
            } finally {
                setLoading(false); // Turn off loading
            }
        };
        getUnits();
    }, []);

    // Loading state
    if (loading) {
        return <p>Loading...</p>;
    }

    // Error state
    if (error) {
        return <p>Error: {error}</p>;
    }

    // Render the UI
    return (
        <div className="unit-list">
            <h1>Unit List</h1>
            <ul>
                {units.map((unit) => (
                    <li key={unit.id} className="unit-item">
                        <h2>{unit.title}</h2>
                        <p>{unit.description}</p>
                        <p>Level: {unit.level}</p>
                        <p>Order: {unit.order}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

// Export Component
export default UnitList;
