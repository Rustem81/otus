import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('layouts/AuthLayout.vue'),
    children: [{ path: '', component: () => import('pages/LoginPage.vue') }],
    meta: { public: true },
  },
  {
    path: '/onboarding',
    component: () => import('layouts/AuthLayout.vue'),
    children: [{ path: '', component: () => import('pages/OnboardingPage.vue') }],
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue'), meta: { public: true } },
      { path: 'profile', component: () => import('pages/ProfilePage.vue') },
      { path: 'history', component: () => import('pages/HistoryPage.vue') },
      { path: 'blacklist', component: () => import('pages/BlacklistPage.vue') },
      { path: 'admin', component: () => import('pages/AdminPage.vue'), meta: { admin: true } },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
