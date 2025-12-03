<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <span v-if="!authStore.isAuthenticated">
          | <RouterLink to="/login">Login</RouterLink>
          | <RouterLink to="/register">Register</RouterLink>
        </span>
        <span v-else>
          | <RouterLink to="/upload">Upload Receipt</RouterLink>
          | <RouterLink to="/transactions">My Transactions</RouterLink>
          | <a href="#" @click.prevent="authStore.logout()">Logout</a>
        </span>
      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  background-color: #f8f9fa;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 0;
}

nav a.router-link-exact-active {
  color: var(--color-text);
  font-weight: bold;
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  text-decoration: none;
  color: #2c3e50;
}

nav a:first-of-type {
  border: 0;
}

main {
  padding: 2rem;
}
</style>
