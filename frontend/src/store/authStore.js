import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../api/client';

// Turn a failed "get login URL" request into a message that says what actually went wrong
const oauthErrorMessage = (error, provider) => {
  if (!error.response) {
    // No response at all: wrong REACT_APP_API_URL, backend down/asleep, or blocked by CORS
    return `Can't reach the server (${api.defaults.baseURL}). Please try again in a minute.`;
  }
  if (error.response.status === 501) {
    return `${provider} login is not configured on the server`;
  }
  return error.response.data?.detail || `${provider} login failed (error ${error.response.status})`;
};

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

      // Get Google OAuth URL -> { url } or { error: reason to show the user }
      getGoogleAuthUrl: async () => {
        try {
          const response = await api.get('/auth/google');
          return { url: response.data.auth_url };
        } catch (error) {
          console.error('Google auth error:', error);
          return { error: oauthErrorMessage(error, 'Google') };
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

      // Get GitHub OAuth URL -> { url } or { error: reason to show the user }
      getGitHubAuthUrl: async () => {
        try {
          const response = await api.get('/auth/github');
          return { url: response.data.auth_url };
        } catch (error) {
          console.error('GitHub auth error:', error);
          return { error: oauthErrorMessage(error, 'GitHub') };
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
