// src/main.js (Update)

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth' // <--- Import the store

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize the Auth store and set up the Axios interceptor
const authStore = useAuthStore()
authStore.initialize()

app.mount('#app')
