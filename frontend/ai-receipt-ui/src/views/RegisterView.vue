<template>
  <div class="auth-container">
    <h2>User Registration</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="email" required>
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <div class="form-group">
        <label for="role">Role (Optional, for testing)</label>
        <select id="role" v-model="role">
          <option value="BASIC_USER">Basic User</option>
          <option value="RECEIPT_LOGGER">Receipt Logger</option>
          <option value="SYSTEM_ADMIN">System Admin</option>
        </select>
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Registering...' : 'Register' }}
      </button>
      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
    <p>Already have an account? <router-link to="/login">Login here</router-link></p>
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
const role = ref('BASIC_USER'); // Default role
const isLoading = ref(false);
const error = ref('');
const successMessage = ref('');

const handleRegister = async () => {
  isLoading.value = true;
  error.value = '';
  successMessage.value = '';

  try {
    const userData = {
      username: username.value,
      email: email.value,
      password: password.value,
      role: role.value,
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

<style scoped>
.auth-container { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
.form-group { margin-bottom: 15px; }
label { display: block; margin-bottom: 5px; font-weight: bold; }
input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background-color: #42b883; color: white; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
.success-message { color: green; margin-top: 10px; }
.error-message { color: red; margin-top: 10px; }
</style>
