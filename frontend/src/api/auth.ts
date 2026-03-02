import api from './client';
import type { User, TokenResponse } from '@/types/models';

interface AdminLoginRequest {
  emp_id: string;
  password: string;
}

interface UserLoginRequest {
  emp_id: string;
}

export const authApi = {
  /**
   * Admin login with password
   */
  adminLogin: (credentials: AdminLoginRequest) =>
    api.post<{ data: TokenResponse }>('/auth/login/admin', credentials),

  /**
   * Regular user login (employee ID only)
   */
  userLogin: (credentials: UserLoginRequest) =>
    api.post<{ data: TokenResponse }>('/auth/login/user', credentials),

  /**
   * Logout
   */
  logout: () => api.post('/auth/logout'),

  /**
   * Get current user info
   */
  getCurrentUser: () => api.get<{ data: User }>('/auth/me'),
};

export default authApi;
