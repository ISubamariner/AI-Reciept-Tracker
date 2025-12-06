<!--
  RegisterView.vue - User Registration Page

  Handles new user registration with form validation and error handling.
  Uses fintech theme components for consistent styling.
-->

<template>
  <div class="content-body">
    <div class="card" style="max-width: 450px; margin: 0 auto;">
      <div class="card-header">
        <h2 class="card-title text-center">📝 User Registration</h2>
        <p class="card-subtitle text-center">Create your account to get started</p>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleRegister">
          <!-- Username Field -->
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              type="text"
              id="username"
              v-model="username"
              class="form-input"
              placeholder="Choose a username"
              required
            >
          </div>

          <!-- Email Field -->
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <input
              type="email"
              id="email"
              v-model="email"
              class="form-input"
              placeholder="your.email@example.com"
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
              placeholder="Create a strong password"
              required
            >
          </div>

          <!-- Success Alert -->
          <div v-if="successMessage" class="alert alert-success">
            ✓ {{ successMessage }}
          </div>

          <!-- Error Alert -->
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="isLoading">
            {{ isLoading ? '🔄 Registering...' : '📝 Create Account' }}
          </button>
        </form>
      </div>

      <div class="card-footer text-center">
        <p class="text-secondary">
          Already have an account?
          <router-link to="/login" style="color: var(--color-primary); font-weight: var(--font-weight-semibold);">
            Login here
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
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');
const successMessage = ref('');

/**
 * Handle registration form submission
 */
const handleRegister = async () => {
  isLoading.value = true;
  error.value = '';
  successMessage.value = '';

  try {
    const userData = {
      username: username.value,
      email: email.value,
      password: password.value,
      role: 'BASIC_USER',
    };

    await authStore.register(userData);

    successMessage.value = 'Registration successful! Redirecting to login...';

    // Redirect after a short delay
    setTimeout(() => {
      router.push('/login');
    }, 1500);

  } catch (err) {
    error.value = err.message || 'Registration failed. Check if username/email already exists.';
    console.error(err);

  } finally {
    isLoading.value = false;
  }
};
</script>
