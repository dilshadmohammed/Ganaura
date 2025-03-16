import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Axios request interceptor to attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Axios response interceptor to handle invalid tokens
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);

export default api;
