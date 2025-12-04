<!--
  App.vue - Main Application Layout

  This component provides the core layout structure with:
  - Side navigation (fixed left sidebar)
  - Main content area (with header and body)
  - Responsive design (mobile-friendly)

  The layout uses the consolidated fintech theme with the Wildflowers color palette.
  See THEME_DOCUMENTATION.md for detailed usage information.
-->

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref } from 'vue'

const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

/**
 * Toggle mobile menu
 */
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

/**
 * Close mobile menu when navigating
 */
const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<template>
  <div class="app-container">
    <!-- Mobile Overlay (click to close menu) -->
    <div
      v-if="mobileMenuOpen"
      class="mobile-overlay"
      @click="closeMobileMenu"
    ></div>

    <!-- Side Navigation -->
    <aside class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <!-- Sidebar Header with Logo -->
      <div class="sidebar-header">
        <RouterLink to="/" class="sidebar-logo" @click="closeMobileMenu">
          💰 Receipt Tracker
        </RouterLink>
      </div>

      <!-- Sidebar Navigation -->
      <nav class="sidebar-nav">
        <!-- Public Navigation Section -->
        <div class="nav-section" v-if="!authStore.isAuthenticated">
          <div class="nav-section-title">Get Started</div>
          <RouterLink to="/" class="nav-item" @click="closeMobileMenu">
            <span class="nav-item-icon">🏠</span>
            Home
          </RouterLink>
          <RouterLink to="/login" class="nav-item" @click="closeMobileMenu">
            <span class="nav-item-icon">🔐</span>
            Login
          </RouterLink>
          <RouterLink to="/register" class="nav-item" @click="closeMobileMenu">
            <span class="nav-item-icon">📝</span>
            Register
          </RouterLink>
        </div>

        <!-- Authenticated Navigation Section -->
        <div v-else>
          <!-- Main Menu -->
          <div class="nav-section">
            <div class="nav-section-title">Main Menu</div>
            <RouterLink to="/" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">🏠</span>
              Dashboard
            </RouterLink>
            <RouterLink to="/upload" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">📤</span>
              Upload Receipt
            </RouterLink>
            <RouterLink to="/transactions" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">📊</span>
              My Transactions
            </RouterLink>
          </div>

          <!-- Account Section -->
          <div class="nav-section">
            <div class="nav-section-title">Account</div>
            <div class="nav-item" style="cursor: default; opacity: 0.7;">
              <span class="nav-item-icon">👤</span>
              {{ authStore.user?.username || 'User' }}
            </div>
            <a href="#" class="nav-item" @click.prevent="authStore.logout(); closeMobileMenu()">
              <span class="nav-item-icon">🚪</span>
              Logout
            </a>
          </div>
        </div>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Mobile Menu Toggle -->
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        aria-label="Toggle navigation menu"
      >
        <span v-if="!mobileMenuOpen">☰</span>
        <span v-else>✕</span>
      </button>

      <!-- Router View - Page Content -->
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/**
 * App Container Styles
 *
 * These styles complement the base theme and provide
 * app-specific adjustments for the layout.
 */

/* Mobile Menu Toggle Button */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: var(--spacing-md);
  left: var(--spacing-md);
  z-index: 1060;
  background-color: var(--color-primary);
  color: var(--color-text-primary);
  border: var(--border-width) solid var(--color-primary);
  border-radius: var(--border-radius);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-xl);
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.mobile-menu-toggle:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.mobile-menu-toggle:active {
  transform: scale(0.95);
}

/* Active navigation link styling */
.nav-item.router-link-active {
  background-color: rgba(168, 220, 171, 0.2);
  border-left-color: var(--nav-active);
  color: var(--nav-active);
  font-weight: var(--font-weight-semibold);
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Responsive Design - Mobile */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }
}
</style>
