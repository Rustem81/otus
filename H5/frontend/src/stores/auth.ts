import { create } from "zustand";

interface User {
  id: string;
  email: string;
  role: "USER" | "ADMIN";
  is_verified: boolean;
  onboarding_completed: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  fetchUser: () => Promise<boolean>;
}

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json();
        set({ error: err.detail || "Ошибка входа", isLoading: false });
        return false;
      }
      const data = await res.json();
      const token = data.access_token || null;
      if (token) localStorage.setItem("access_token", token);
      localStorage.setItem("onboarding_completed", String(data.user.onboarding_completed ?? true));
      set({ user: data.user, token, isLoading: false });
      return true;
    } catch {
      set({ error: "Сервер недоступен", isLoading: false });
      return false;
    }
  },

  register: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const res = await fetch(`${API}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        const err = await res.json();
        set({ error: err.detail || "Ошибка регистрации", isLoading: false });
        return false;
      }
      set({ isLoading: false });
      return true;
    } catch {
      set({ error: "Сервер недоступен", isLoading: false });
      return false;
    }
  },

  logout: () => {
    const token = get().token;
    fetch(`${API}/api/v1/auth/logout`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }).catch(() => {});
    localStorage.removeItem("access_token");
    localStorage.removeItem("onboarding_completed");
    set({ user: null, token: null });
  },

  fetchUser: async () => {
    const token = get().token;
    if (!token) return false;
    try {
      const res = await fetch(`${API}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return false;
      const user = await res.json();
      localStorage.setItem("onboarding_completed", String(user.onboarding_completed ?? true));
      set({ user });
      return true;
    } catch {
      return false;
    }
  },
}));
