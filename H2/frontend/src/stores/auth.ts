import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  loginApiV1AuthLoginPost,
  registerApiV1AuthRegisterPost,
  logoutApiV1AuthLogoutPost,
  getCurrentUserInfoApiV1AuthMeGet,
} from 'src/api/auth/auth';
import type { UserResponse } from 'src/api/client.schemas';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserResponse | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN');

  async function login(credentials: { email: string; password: string }) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await loginApiV1AuthLoginPost(credentials);
      user.value = response.user;
      // Save token if returned (MVP bearer auth)
      const resp = response as Record<string, unknown>;
      if (resp.access_token) {
        localStorage.setItem('access_token', resp.access_token as string);
      }
      localStorage.setItem('onboarding_completed', String(user.value.onboarding_completed ?? true));
      return true;
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      error.value = e.response?.data?.detail || 'Ошибка входа';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(credentials: { email: string; password: string }) {
    isLoading.value = true;
    error.value = null;
    try {
      await registerApiV1AuthRegisterPost(credentials);
      return true;
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      error.value = e.response?.data?.detail || 'Ошибка регистрации';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    try {
      await logoutApiV1AuthLogoutPost();
    } finally {
      user.value = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('onboarding_completed');
    }
  }

  async function fetchUser() {
    try {
      const data = await getCurrentUserInfoApiV1AuthMeGet();
      user.value = data;
      localStorage.setItem('onboarding_completed', String(data.onboarding_completed ?? true));
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
