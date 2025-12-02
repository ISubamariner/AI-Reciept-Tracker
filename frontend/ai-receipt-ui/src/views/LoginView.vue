<template>
  <div class="auth-container">
    <h2>User Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Logging In...' : 'Login' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
    <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // @ is a webpack alias for /src

const authStore = useAuthStore();
const router = useRouter();

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

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

    // Redirect to the home page or a protected area upon successful login
    router.push('/');

  } catch (err) {
    // Display error message from the backend (e.g., Invalid credentials)
    error.value = err.message || 'Login failed. Please check your credentials.';
    console.error(err);

  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.auth-container { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
.form-group { margin-bottom: 15px; }
label { display: block; margin-bottom: 5px; font-weight: bold; }
input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background-color: #42b883; color: white; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
button:hover:not(:disabled) { background-color: #368266; }
button:disabled { background-color: #a5d8c6; cursor: not-allowed; }
.error-message { color: red; margin-top: 10px; }
</style>
