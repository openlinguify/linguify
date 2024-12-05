import axios from "axios";

const API_URL = "http://localhost:8000/api/data/";

export const fetchCourses = async () => {
  try {
    const response = await axios.get(`${API_URL}courses/`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des cours :", error);
    throw error;
  }
};

export const fetchCategories = async () => {
  try {
    const response = await axios.get(`${API_URL}categories/`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des catégories :", error);
    throw error;
  }
};
