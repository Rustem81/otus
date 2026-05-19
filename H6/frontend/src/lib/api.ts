const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getCsrfToken(): string | null {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : null;
}

function getHeaders(method?: string): HeadersInit {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = localStorage.getItem("access_token");
  if (token) headers["Authorization"] = `Bearer ${token}`;

  // Add CSRF token for mutating requests
  if (method && ["POST", "PUT", "DELETE", "PATCH"].includes(method.toUpperCase())) {
    const csrf = getCsrfToken();
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }

  return headers;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const method = init?.method || "GET";
  const res = await fetch(`${API}${path}`, {
    ...init,
    credentials: "include", // Send cookies (csrf_token)
    headers: { ...getHeaders(method), ...init?.headers },
  });
  if (res.status === 401) {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Ошибка сервера" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export function apiGet<T>(path: string) {
  return apiFetch<T>(path);
}

export function apiPost<T>(path: string, body?: unknown) {
  return apiFetch<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export function apiPut<T>(path: string, body?: unknown) {
  return apiFetch<T>(path, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });
}

export function apiDelete<T>(path: string) {
  return apiFetch<T>(path, { method: "DELETE" });
}
