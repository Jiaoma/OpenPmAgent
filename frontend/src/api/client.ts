import axios, { AxiosInstance, AxiosError } from 'axios';
import type { APIResponse } from '@/types/models';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error: AxiosError<APIResponse>) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error.response?.data || error.message);
      }
    );
  }

  get<T = any>(url: string, config?: any): Promise<APIResponse<T>> {
    return this.client.get(url, config);
  }

  post<T = any>(url: string, data?: any, config?: any): Promise<APIResponse<T>> {
    return this.client.post(url, data, config);
  }

  put<T = any>(url: string, data?: any, config?: any): Promise<APIResponse<T>> {
    return this.client.put(url, data, config);
  }

  delete<T = any>(url: string, config?: any): Promise<APIResponse<T>> {
    return this.client.delete(url, config);
  }
}

// Create and export API client instance
export const apiClient = new ApiClient();

// Export individual methods for convenience
export const api = {
  get: <T = any>(url: string, config?: any) => apiClient.get<T>(url, config),
  post: <T = any>(url: string, data?: any, config?: any) => apiClient.post<T>(url, data, config),
  put: <T = any>(url: string, data?: any, config?: any) => apiClient.put<T>(url, data, config),
  delete: <T = any>(url: string, config?: any) => apiClient.delete<T>(url, config),
};

// Alias for backwards compatibility

// Alias for backwards compatibility
export const client = api;

export default api;
