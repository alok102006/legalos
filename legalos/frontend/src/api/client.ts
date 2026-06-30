import axios from 'axios';

// Get base URL from Vite environment, default to localhost FastAPI port
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject User Role header on every request automatically
apiClient.interceptors.request.use(
  (config) => {
    const role = localStorage.getItem('legalos_fake_role') || 'owner';
    config.headers['X-User-Role'] = role;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
