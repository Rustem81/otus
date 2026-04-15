import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';

// Pages that don't require authentication
const publicPages = new Set(['/login', '/']);

// Simple auth check using cookie or localStorage token
function hasAuthCookie(): boolean {
  return document.cookie.includes('session_token=') || !!localStorage.getItem('access_token');
}

// Check if onboarding is completed (stored after login/fetchUser)
function isOnboardingCompleted(): boolean {
  try {
    const raw = localStorage.getItem('onboarding_completed');
    return raw === 'true';
  } catch {
    return true; // Default to true to avoid redirect loops
  }
}

export async function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  const isPublicPage = to.meta.public === true || publicPages.has(to.path);
  const requiresAdmin = to.meta.admin === true;
  const isAuthenticated = hasAuthCookie();

  // Not authenticated and trying to access protected page
  if (!isAuthenticated && !isPublicPage) {
    return next({
      path: '/login',
      query: { redirect: to.fullPath },
    });
  }

  // Already authenticated and trying to access login
  if (isAuthenticated && to.path === '/login') {
    return next('/');
  }

  // Redirect to onboarding if not completed (skip for onboarding page itself and public pages)
  if (isAuthenticated && !isOnboardingCompleted() && to.path !== '/onboarding' && !isPublicPage) {
    return next('/onboarding');
  }

  // Admin check - will be handled by component or API
  if (requiresAdmin && !isAuthenticated) {
    return next('/');
  }

  next();
}
