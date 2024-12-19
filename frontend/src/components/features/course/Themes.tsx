// frontend/src/components/features/course/Themes.tsx

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

// Define the Theme type
interface Theme {
    id: string;
    name: string;
}

const Themes: React.FC = () => {
    const [themes, setThemes] = useState<Theme[]>([]); // Add type to themes

    useEffect(() => {
        axios
            .get<Theme[]>("/api/themes/") // Specify the expected response type
            .then((response) => setThemes(response.data))
            .catch((error) => console.error("Erreur:", error));
    }, []);

    return (
        <div>
            <h1>Thèmes</h1>
            <ul>
                {themes.map((theme) => (
                    <li key={theme.id}>
                        <Link to={`/theme/${theme.id}`}>{theme.name}</Link>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Themes;


