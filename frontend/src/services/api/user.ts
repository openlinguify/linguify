import axios from "axios";

const API_URL = "http://localhost:8000/api/user/";

export const fetchUserProfile = async () => {
  try {
    const response = await axios.get(`${API_URL}profile/`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération du profil utilisateur :", error);
    throw error;
  }
};

export const updateUserProfile = async (profileData: { name?: string; email?: string }) => {
  try {
    const response = await axios.put(`${API_URL}profile/`, profileData);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la mise à jour du profil utilisateur :", error);
    throw error;
  }
};

export const fetchUserCourses = async () => {
  try {
    const response = await axios.get(`${API_URL}courses/`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des cours utilisateur :", error);
    throw error;
  }
};
