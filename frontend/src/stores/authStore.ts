import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types/models';
import { authApi } from '@/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (empId: string, password?: string) => Promise<void>;
  adminLogin: (empId: string, password: string) => Promise<void>;
  userLogin: (empId: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isAdmin: false,
      isLoading: false,
      error: null,

      // Admin login
      adminLogin: async (empId: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.adminLogin({ emp_id: empId, password });
          const { access_token, user } = response.data || { access_token: null, user: null };
          
          localStorage.setItem('access_token', access_token);
          set({
            token: access_token,
            user,
            isAuthenticated: true,
            isAdmin: user?.is_admin || false,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed',
          });
          throw error;
        }
      },

      // Regular user login
      userLogin: async (empId: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.userLogin({ emp_id: empId });
          const { access_token, user } = response.data || { access_token: null, user: null };
          
          localStorage.setItem('access_token', access_token);
          set({
            token: access_token,
            user,
            isAuthenticated: true,
            isAdmin: user?.is_admin || false,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed',
          });
          throw error;
        }
      },

      // Generic login (auto-detect admin/user)
      login: async (empId: string, password?: string) => {
        if (password) {
          return get().adminLogin(empId, password);
        } else {
          return get().userLogin(empId);
        }
      },

      // Logout
      logout: async () => {
        try {
          await authApi.logout();
        } catch (error) {
          // Ignore logout errors
        }
        localStorage.removeItem('access_token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isAdmin: false,
        });
      },

      // Fetch current user info
      fetchUser: async () => {
        try {
          const response = await authApi.getCurrentUser();
          set({ user: response.data?.user || response.data || null });
        } catch (error) {
          // User might not be authenticated
          console.error('Failed to fetch user:', error);
        }
      },

      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        isAdmin: state.isAdmin,
      }),
    }
  )
);

export default useAuthStore;
