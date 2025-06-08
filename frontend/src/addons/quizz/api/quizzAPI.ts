// src/addons/quizz/api/quizzAPI.ts
import apiClient from '@/core/api/apiClient';
import { Quiz, QuizSession, Question, Answer } from '../types';

const quizzAPI = {
  // Quiz CRUD operations
  getAll: async () => {
    try {
      const response = await apiClient.get('/api/v1/quizz/');
      return response.data;
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
      throw err;
    }
  },

  getById: async (id: number) => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/${id}/`);
      return response.data;
    } catch (err) {
      console.error(`Failed to fetch quiz #${id}:`, err);
      throw err;
    }
  },

  create: async (data: Partial<Quiz>) => {
    try {
      const response = await apiClient.post('/api/v1/quizz/', data);
      return response.data;
    } catch (err) {
      console.error('Failed to create quiz:', err);
      throw err;
    }
  },

  update: async (id: number, data: Partial<Quiz>) => {
    try {
      const response = await apiClient.patch(`/api/v1/quizz/${id}/`, data);
      return response.data;
    } catch (err) {
      console.error(`Failed to update quiz #${id}:`, err);
      throw err;
    }
  },

  delete: async (id: number) => {
    try {
      await apiClient.delete(`/api/v1/quizz/${id}/`);
      return true;
    } catch (err) {
      console.error(`Failed to delete quiz #${id}:`, err);
      throw err;
    }
  },

  // Quiz session management
  startSession: async (quizId: number) => {
    try {
      const response = await apiClient.post(`/api/v1/quizz/${quizId}/start_session/`);
      return response.data;
    } catch (err) {
      console.error('Failed to start quiz session:', err);
      throw err;
    }
  },

  submitAnswer: async (quizId: number, sessionId: number, questionId: number, answerId?: number, textAnswer?: string) => {
    try {
      const response = await apiClient.post(`/api/v1/quizz/${quizId}/submit_answer/`, {
        session_id: sessionId,
        question_id: questionId,
        answer_id: answerId,
        text_answer: textAnswer || '',
      });
      return response.data;
    } catch (err) {
      console.error('Failed to submit answer:', err);
      throw err;
    }
  },

  completeSession: async (quizId: number, sessionId: number) => {
    try {
      const response = await apiClient.post(`/api/v1/quizz/${quizId}/complete_session/`, {
        session_id: sessionId,
      });
      return response.data;
    } catch (err) {
      console.error('Failed to complete session:', err);
      throw err;
    }
  },

  // User sessions
  getMySessions: async () => {
    try {
      const response = await apiClient.get('/api/v1/quizz/my_sessions/');
      return response.data;
    } catch (err) {
      console.error('Failed to fetch user sessions:', err);
      throw err;
    }
  },

  // Categories
  getCategories: async () => {
    try {
      const response = await apiClient.get('/api/v1/quizz/categories/');
      return response.data;
    } catch (err) {
      console.error('Failed to fetch categories:', err);
      throw err;
    }
  },

  // Filter quizzes
  getByCategory: async (category: string) => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/?category=${category}`);
      return response.data;
    } catch (err) {
      console.error('Failed to fetch quizzes by category:', err);
      throw err;
    }
  },

  getByDifficulty: async (difficulty: string) => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/?difficulty=${difficulty}`);
      return response.data;
    } catch (err) {
      console.error('Failed to fetch quizzes by difficulty:', err);
      throw err;
    }
  },
};

export default quizzAPI;
