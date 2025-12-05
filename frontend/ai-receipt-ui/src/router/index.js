// src/router/index.js (Updated with Authentication Guards)

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue'; // Import new views
import RegisterView from '../views/RegisterView.vue';
import ReceiptUploadView from '../views/ReceiptUploadView.vue';
import TransactionsView from '../views/TransactionsView.vue';
import UserManagementView from '../views/UserManagementView.vue';
import AuditLogsView from '../views/AuditLogsView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView, // Point path to the Login component
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView, // Point path to the Register component
    },
    {
      path: '/upload',
      name: 'upload',
      component: ReceiptUploadView,
      meta: { requiresAuth: true }
    },
    {
      path: '/transactions',
      name: 'transactions',
      component: TransactionsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: UserManagementView,
      meta: { requiresAuth: true, requiredRole: 'System Admin' }
    },
    {
      path: '/audit-logs',
      name: 'audit-logs',
      component: AuditLogsView,
      meta: { requiresAuth: true, requiredRole: 'System Admin' }
    },
  ],
});

// Global Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.meta.requiresAuth;
  const requiredRole = to.meta.requiredRole;

  if (requiresAuth && !authStore.isAuthenticated) {
    // If route requires auth and user is NOT logged in, redirect to login
    next('/login');
  } else if (requiresAuth && requiredRole && authStore.currentUserRole !== requiredRole) {
    // If route requires a specific role and user does not have it, redirect home
    // A better implementation would show a 403 Forbidden page
    console.warn(`Access denied for role: ${authStore.currentUserRole}. Required: ${requiredRole}`);
    next('/');
  } else {
    // Proceed as normal
    next();
  }
});

export default router;
