import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router';

// Pages that don't require authentication
const publicPages = new Set(['/login', '/']);

// Simple auth check using cookie
function hasAuthCookie(): boolean {
  return document.cookie.includes('session_token=');
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

  // Admin check - will be handled by component or API
  if (requiresAdmin && !isAuthenticated) {
    return next('/');
  }

  next();
}
