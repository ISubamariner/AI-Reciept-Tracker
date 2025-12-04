<!--
  LoginView.vue - User Login Page

  Handles user authentication with form validation and error handling.
  Uses fintech theme components for consistent styling.
-->

<template>
  <div class="content-body">
    <div class="card" style="max-width: 450px; margin: 0 auto;">
      <div class="card-header">
        <h2 class="card-title text-center">🔐 User Login</h2>
        <p class="card-subtitle text-center">Sign in to access your account</p>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleLogin">
          <!-- Username Field -->
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              id="username"
              v-model="username"
              class="form-input"
              placeholder="Enter your username"
              required
            >
          </div>

          <!-- Password Field -->
          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input
              type="password"
              id="password"
              v-model="password"
              class="form-input"
              placeholder="Enter your password"
              required
            >
          </div>

          <!-- Error Alert -->
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="isLoading">
            {{ isLoading ? '🔄 Logging In...' : '🔐 Login' }}
          </button>
        </form>
      </div>

      <div class="card-footer text-center">
        <p class="text-secondary">
          Don't have an account?
          <router-link to="/register" style="color: var(--color-primary); font-weight: var(--font-weight-semibold);">
            Register here
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

/**
 * Handle login form submission
 */
const handleLogin = async () => {
  isLoading.value = true;
  error.value = '';

  try {
    const credentials = {
      username: username.value,
      password: password.value,
    };

    // Call the login action in the Pinia store
    await authStore.login(credentials);

    // Redirect to the home page upon successful login
    router.push('/');

  } catch (err) {
    // Display error message from the backend
    error.value = err.message || 'Login failed. Please check your credentials.';
    console.error(err);

  } finally {
    isLoading.value = false;
  }
};
</script>
