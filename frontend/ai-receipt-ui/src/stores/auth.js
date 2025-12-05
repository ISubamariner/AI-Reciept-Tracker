import { defineStore } from 'pinia';
import axios from 'axios';

// Get the base API URL from the environment variables
const API_URL = import.meta.env.VITE_API_BASE_URL;

export const useAuthStore = defineStore('auth', {
    state: () => ({
        // Try to load token and user data from localStorage on app startup
        token: localStorage.getItem('token') || null,
        user: JSON.parse(localStorage.getItem('user')) || null,
        isLoggedIn: !!localStorage.getItem('token'),
        role: localStorage.getItem('role') || null,
    }),

    getters: {
        // Simple check to see if the user has a valid token
        isAuthenticated: (state) => state.isLoggedIn,
        currentUserRole: (state) => state.role,
    },

    actions: {
        // --- 1. Login Action ---
        async login(credentials) {
            try {
                const response = await axios.post(`${API_URL}/auth/login`, credentials);

                const token = response.data.access_token;

                // Decode the JWT to get user details (role, username)
                // In a real app, you would verify this server-side,
                // but we extract basic info here for display purposes.
                const userPayload = JSON.parse(atob(token.split('.')[1]));

                this.token = token;
                this.user = {
                    username: userPayload.username,
                    id: userPayload.user_id,
                    role: userPayload.role
                };
                this.role = userPayload.role;
                this.isLoggedIn = true;

                // Persist state in browser storage
                localStorage.setItem('token', token);
                localStorage.setItem('user', JSON.stringify(this.user));
                localStorage.setItem('role', this.role);

                return response.data;

            } catch (error) {
                this.logout(); // Clear state if login fails
                throw error.response ? error.response.data : error;
            }
        },

        // --- 2. Registration Action ---
        async register(userData) {
            try {
                const response = await axios.post(`${API_URL}/auth/register`, userData);

                // After successful registration, you typically log the user in or redirect them.
                // For simplicity, we just return success.
                return response.data;

            } catch (error) {
                throw error.response ? error.response.data : error;
            }
        },

        // --- 3. Logout Action ---
        logout() {
            this.token = null;
            this.user = null;
            this.role = null;
            this.isLoggedIn = false;

            // Clear storage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('role');

            // Optionally redirect user to the login page after clearing state
            // Example: router.push('/login');
        },

        // --- 4. Axios Interceptor for Token Injection ---
        initialize() {
            // Set up an Axios interceptor to automatically add the JWT to every API request
            axios.interceptors.request.use(config => {
                if (this.token) {
                    config.headers.Authorization = `Bearer ${this.token}`;
                }
                return config;
            }, error => {
                return Promise.reject(error);
            });
        }
    }
});
