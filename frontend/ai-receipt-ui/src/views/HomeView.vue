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
  <div class="home-container">
    <h1>Welcome to AI Receipt Tracker</h1>
    <p>Manage your expenses effortlessly.</p>

    <div v-if="authStore.isAuthenticated">
      <p>Hello, {{ authStore.user?.username }}!</p>
      <button @click="logout">Logout</button>
      <br><br>
      <router-link to="/upload">Go to Receipt Upload</router-link>
    </div>
    <div v-else>
      <p>Please log in to continue.</p>
      <router-link to="/login">Login</router-link> |
      <router-link to="/register">Register</router-link>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 50px;
}
</style>
