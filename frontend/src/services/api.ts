// frontend/src/services/api.ts

import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/v1/course/units/";

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

export const fetchLevels = async () => {
    const token = localStorage.getItem("token");
    const headers = {
        Authorization: `Token ${token}`,
    };

    const response = await axios.get('${API_URL}levels/', { headers });
    return response.data;
};

// Fetch Units
export const fetchUnits = async () => {
    try {
        const token = localStorage.getItem("token");
        const response = await apiClient.get("units/", {
            headers: {
                Authorization: `Token ${token}`,
            },
        });
        return response.data;
    } catch (error: any) {
        console.error("Error fetching units:", error.response || error.message);
        throw error;
    }
};
