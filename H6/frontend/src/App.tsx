import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppErrorBoundary } from "@/components/ErrorBoundary";
import { MainLayout } from "@/layouts/main-layout";
import { AuthLayout } from "@/layouts/auth-layout";
import { LoginPage } from "@/pages/login";
import { AuthCallbackPage } from "@/pages/auth-callback";
import { OnboardingPage } from "@/pages/onboarding";
import { MainPage } from "@/pages/main";
import { ProfilePage } from "@/pages/profile";
import { HistoryPage } from "@/pages/history";
import { BlacklistPage } from "@/pages/blacklist";
import { AdminPage } from "@/pages/admin";
import { useAuthStore } from "@/stores/auth";
import { useEffect } from "react";
import { trackPageView } from "@/lib/analytics";

const queryClient = new QueryClient();

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  const { token, fetchUser } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    if (token) fetchUser();
  }, [token, fetchUser]);

  useEffect(() => {
    trackPageView(location.pathname + location.search);
  }, [location]);

  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>
      <Route path="/auth/callback" element={<AuthCallbackPage />} />
      <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/" element={<MainPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/blacklist" element={<BlacklistPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AppErrorBoundary>
          <BrowserRouter>
            <div className="dark">
              <AppRoutes />
            </div>
          </BrowserRouter>
        </AppErrorBoundary>
      </TooltipProvider>
    </QueryClientProvider>
  );
}
