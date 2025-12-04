<!--
  HomeView.vue - Dashboard/Home Page

  Displays welcome message and quick actions based on authentication status.
  Uses fintech theme components for consistent styling.
-->

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

function logout() {
  authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="content-body">
    <!-- Hero Section -->
    <div class="card text-center mb-4">
      <div class="card-body">
        <h1 class="mb-3">💰 AI Receipt Tracker</h1>
        <p class="text-secondary" style="font-size: 1.125rem;">
          Manage your expenses effortlessly with AI-powered receipt processing
        </p>
      </div>
    </div>

    <!-- Authenticated User Section -->
    <div v-if="authStore.isAuthenticated">
      <!-- Welcome Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h2 class="card-title">Welcome back, {{ authStore.user?.username }}! 👋</h2>
          <p class="card-subtitle">Ready to manage your receipts?</p>
        </div>
        <div class="card-body">
          <div class="d-flex gap-3" style="flex-wrap: wrap;">
            <router-link to="/upload" class="btn btn-primary btn-lg">
              📤 Upload Receipt
            </router-link>
            <router-link to="/transactions" class="btn btn-secondary btn-lg">
              📊 View Transactions
            </router-link>
          </div>
        </div>
      </div>

      <!-- Features Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--spacing-lg);">
        <!-- Feature 1 -->
        <div class="card">
          <div class="card-body">
            <h3 class="mb-2">🤖 AI-Powered</h3>
            <p class="text-secondary">
              Our advanced AI automatically extracts transaction details from your receipts.
            </p>
          </div>
        </div>

        <!-- Feature 2 -->
        <div class="card">
          <div class="card-body">
            <h3 class="mb-2">📈 Track Expenses</h3>
            <p class="text-secondary">
              Keep all your transactions organized and easily accessible in one place.
            </p>
          </div>
        </div>

        <!-- Feature 3 -->
        <div class="card">
          <div class="card-body">
            <h3 class="mb-2">🔒 Secure</h3>
            <p class="text-secondary">
              Your financial data is protected with enterprise-grade security.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Guest User Section -->
    <div v-else>
      <div class="card" style="max-width: 500px; margin: 0 auto;">
        <div class="card-header">
          <h2 class="card-title text-center">Get Started</h2>
          <p class="card-subtitle text-center">Please log in or create an account to continue</p>
        </div>
        <div class="card-body">
          <div class="d-flex flex-column gap-3">
            <router-link to="/login" class="btn btn-primary btn-lg btn-block">
              🔐 Login
            </router-link>
            <router-link to="/register" class="btn btn-outline btn-lg btn-block">
              📝 Create Account
            </router-link>
          </div>
        </div>
      </div>

      <!-- Benefits Section -->
      <div class="mt-5">
        <h3 class="text-center mb-4">Why Choose AI Receipt Tracker?</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--spacing-lg);">
          <div class="card text-center">
            <div class="card-body">
              <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">⚡</div>
              <h4>Fast Processing</h4>
              <p class="text-secondary">Upload and process receipts in seconds</p>
            </div>
          </div>
          <div class="card text-center">
            <div class="card-body">
              <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">💼</div>
              <h4>Professional</h4>
              <p class="text-secondary">Built for individuals and businesses</p>
            </div>
          </div>
          <div class="card text-center">
            <div class="card-body">
              <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">📱</div>
              <h4>Accessible</h4>
              <p class="text-secondary">Access your data from anywhere</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
