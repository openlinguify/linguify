import axios from 'axios';

const API_URL = 'http://localhost:8000'; // Assurez-vous que l'URL pointe vers votre backend

export const updateWordStatus = (word, status) => {
    return axios.post(`${API_URL}/update_word_status/`, {
        word: word,
        status: status,
    });
};

export const getThemes = () => {
    return axios.get(`${API_URL}/themes/`);
};

export const getUnits = () => {
    return axios.get(`${API_URL}/units/`);
};

export const getExercises = () => {
    return axios.get(`${API_URL}/exercises/`);
};
