import axios from "axios";

const API_URL = "http://localhost:8000/api/auth/";

export const login = async (email: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}login/`, { email, password });
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la connexion :", error);
    throw error;
  }
};

export const register = async (userData: { name: string; email: string; password: string }) => {
  try {
    const response = await axios.post(`${API_URL}register/`, userData);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'inscription :", error);
    throw error;
  }
};

export const logout = async () => {
  try {
    await axios.post(`${API_URL}logout/`);
  } catch (error) {
    console.error("Erreur lors de la déconnexion :", error);
    throw error;
  }
};
