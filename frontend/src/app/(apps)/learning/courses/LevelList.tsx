// frontend/src/app/%28course%29/%28routes%29/course/LevelList.tsx

import React, { useEffect, useState } from 'react';
import { fetchLevels } from '@services/api';

interface Level {
    id: number;
    name: string;
    order: number;
}

const LevelList: React.FC = () => {
    const [levels, setLevels] = useState<Level[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getLevels = async () => {
            try {
                const data = await fetchLevels();
                setLevels(data as Level[]);
            } catch (err) {
                setError('Failed to load levels');
            } finally {
                setLoading(false);
            }
        };
        getLevels();
    }, []);

    if (loading) {
        return <p>Loading...</p>;
    }

    if (error) {
        return <p>Error: {error}</p>;
    }

    return (
        <div className="level-list">
            <h1>Levels</h1>
            <ul>
                {levels.map((level) => (
                    <li key={level.id}>
                        <h2>{level.name}</h2>
                        <p>Order: {level.order}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default LevelList;
