import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/client';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Set tokens and user
      setAuth: (data) => {
        set({
          user: data.user,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
          error: null,
        });
        // Set token in axios headers
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      },

      // Clear auth state
      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
        delete api.defaults.headers.common['Authorization'];
      },

      // Signup with email and password
      signup: async (email, password, fullName) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/signup', {
            email,
            password,
            full_name: fullName,
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const message = error.response?.data?.detail || 'Signup failed';
          set({ error: message, isLoading: false });
          return { success: false, error: message };
        } finally {
          set({ isLoading: false });
        }
      },

      // Login with email and password
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/login', {
            email,
            password,
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const message = error.response?.data?.detail || 'Login failed';
          set({ error: message, isLoading: false });
          return { success: false, error: message };
        } finally {
          set({ isLoading: false });
        }
      },

      // Logout
      logout: () => {
        get().clearAuth();
      },

      // Get Google OAuth URL
      getGoogleAuthUrl: async () => {
        try {
          const response = await api.get('/auth/google');
          return response.data.auth_url;
        } catch (error) {
          console.error('Google auth error:', error);
          return null;
        }
      },

      // Handle Google OAuth callback
      handleGoogleCallback: async (code) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/google/callback', null, {
            params: { code },
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const message = error.response?.data?.detail || 'Google login failed';
          set({ error: message, isLoading: false });
          return { success: false, error: message };
        } finally {
          set({ isLoading: false });
        }
      },

      // Get GitHub OAuth URL
      getGitHubAuthUrl: async () => {
        try {
          const response = await api.get('/auth/github');
          return response.data.auth_url;
        } catch (error) {
          console.error('GitHub auth error:', error);
          return null;
        }
      },

      // Handle GitHub OAuth callback
      handleGitHubCallback: async (code) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/github/callback', null, {
            params: { code },
          });
          get().setAuth(response.data);
          return { success: true };
        } catch (error) {
          const message = error.response?.data?.detail || 'GitHub login failed';
          set({ error: message, isLoading: false });
          return { success: false, error: message };
        } finally {
          set({ isLoading: false });
        }
      },

      // Refresh access token
      refreshAccessToken: async () => {
        const refreshToken = get().refreshToken;
        if (!refreshToken) {
          get().clearAuth();
          return false;
        }
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          });
          get().setAuth(response.data);
          return true;
        } catch (error) {
          get().clearAuth();
          return false;
        }
      },

      // Get current user
      fetchUser: async () => {
        try {
          const response = await api.get('/auth/me');
          set({ user: response.data });
          return response.data;
        } catch (error) {
          if (error.response?.status === 401) {
            // Try to refresh token
            const refreshed = await get().refreshAccessToken();
            if (refreshed) {
              return get().fetchUser();
            }
          }
          get().clearAuth();
          return null;
        }
      },

      // Initialize auth from stored token
      initAuth: () => {
        const token = get().accessToken;
        if (token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
