import { apiClient } from './apiClient';

// Types
export interface Department {
  id: number;
  name: string;
  description: string;
  position_count: number;
}

export interface JobPosition {
  id: number;
  title: string;
  department_name?: string;
  department?: Department;
  location: string;
  employment_type: string;
  experience_level: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  benefits?: string;
  salary_range?: string;
  application_email?: string;
  application_url?: string;
  posted_date: string;
  closing_date?: string;
  is_featured: boolean;
  is_open: boolean;
  application_count?: number;
}

export interface JobApplication {
  position: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  cover_letter?: string;
  resume_file?: File;
  resume_url?: string;
  portfolio_url?: string;
  linkedin_url?: string;
}

export interface JobStats {
  total_positions: number;
  departments: number;
  featured_positions: number;
}

// API Functions
export const jobsApi = {
  // Get all departments
  getDepartments: async (): Promise<Department[]> => {
    const response = await apiClient.get('/api/v1/jobs/departments/');
    return response.data;
  },

  // Get all job positions with optional filtering
  getJobPositions: async (params?: {
    department?: number;
    employment_type?: string;
    experience_level?: string;
    location?: string;
    search?: string;
  }): Promise<JobPosition[]> => {
    const response = await apiClient.get('/api/v1/jobs/positions/', { params });
    return response.data;
  },

  // Get job position details
  getJobPosition: async (id: number): Promise<JobPosition> => {
    const response = await apiClient.get(`/api/v1/jobs/positions/${id}/`);
    return response.data;
  },

  // Submit job application
  submitApplication: async (application: JobApplication): Promise<{ message: string; application_id: number }> => {
    // Create FormData if there's a file, otherwise use JSON
    if (application.resume_file) {
      const formData = new FormData();
      Object.entries(application).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (key === 'resume_file' && value instanceof File) {
            formData.append(key, value);
          } else {
            formData.append(key, value.toString());
          }
        }
      });
      const response = await apiClient.post('/api/v1/jobs/apply/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } else {
      // Remove resume_file from data if no file
      const { resume_file, ...applicationData } = application;
      const response = await apiClient.post('/api/v1/jobs/apply/', applicationData);
      return response.data;
    }
  },

  // Get job statistics
  getJobStats: async (): Promise<JobStats> => {
    const response = await apiClient.get('/api/v1/jobs/stats/');
    return response.data;
  },
};

// Helper functions
export const formatEmploymentType = (type: string): string => {
  const types: { [key: string]: string } = {
    'full_time': 'Full Time',
    'part_time': 'Part Time',
    'contract': 'Contract',
    'internship': 'Internship',
    'remote': 'Remote',
  };
  return types[type] || type;
};

export const formatExperienceLevel = (level: string): string => {
  const levels: { [key: string]: string } = {
    'entry': 'Entry Level',
    'mid': 'Mid Level',
    'senior': 'Senior Level',
    'lead': 'Lead',
    'manager': 'Manager',
  };
  return levels[level] || level;
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};