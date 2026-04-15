import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from 'boot/axios';

interface User {
  id: string;
  email: string;
  role: 'USER' | 'ADMIN';
  is_verified: boolean;
  onboarding_completed: boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN');

  // Actions
  async function login(credentials: LoginCredentials) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/login', credentials);
      user.value = response.data.user;
      // Save token for MVP auth
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }
      // Persist onboarding status for router guard
      localStorage.setItem('onboarding_completed', String(response.data.user.onboarding_completed ?? true));
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка входа';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(credentials: RegisterCredentials) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/register', credentials);
      user.value = response.data.user;
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка регистрации';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout');
    } finally {
      user.value = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('onboarding_completed');
    }
  }

  async function fetchUser() {
    try {
      const response = await api.get('/auth/me');
      user.value = response.data;
      localStorage.setItem('onboarding_completed', String(response.data.onboarding_completed ?? true));
      return true;
    } catch {
      user.value = null;
      return false;
    }
  }

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchUser,
  };
});
