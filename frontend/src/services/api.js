import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API endpoints
export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  getCurrentUser: () => apiClient.get('/auth/me'),
};

export const projectsAPI = {
  create: (data) => apiClient.post('/projects', data),
  list: () => apiClient.get('/projects'),
  get: (id) => apiClient.get(`/projects/${id}`),
  update: (id, data) => apiClient.put(`/projects/${id}`, data),
  delete: (id) => apiClient.delete(`/projects/${id}`),
};

export const assetsAPI = {
  getPresignedUrl: (data) => apiClient.post('/assets/presigned-url', data),
  create: (projectId, data) => apiClient.post(`/assets/${projectId}`, data),
  list: (projectId) => apiClient.get(`/assets/project/${projectId}`),
  delete: (id) => apiClient.delete(`/assets/${id}`),
};

export const jobsAPI = {
  startEdit: (data) => apiClient.post('/jobs/start-edit', data),
  getStatus: (id) => apiClient.get(`/jobs/${id}`),
  getLatest: (projectId) => apiClient.get(`/jobs/project/${projectId}/latest`),
};
