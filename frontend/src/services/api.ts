// frontend/src/services/api.ts

import axios from "axios";

const API_URL = "http://localhost:8000/api/v1/units";


export const fetchLevels = async () => {
    const token = localStorage.getItem("token");
    const headers = {
        Authorization: `Token ${token}`,
    };

    const response = await axios.get('${API_URL}levels/', { headers });
    return response.data;
};

export const fetchUnits = async () => {
    const token = localStorage.getItem("token");
    const headers = {
        Authorization: `Token ${token}`,
    };
    const response = await axios.get(API_URL, { headers });
    return response.data;
};

