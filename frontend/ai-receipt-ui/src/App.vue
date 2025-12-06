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
import { useCurrencyStore } from '@/stores/currency'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import CurrencySelector from '@/components/CurrencySelector.vue'

const authStore = useAuthStore()
const currencyStore = useCurrencyStore()
const mobileMenuOpen = ref(false)
const currentTime = ref(new Date())
let clockInterval = null

/**
 * Get timezone abbreviation from browser
 */
const getTimezone = () => {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  return timezone
}

/**
 * Format current time with timezone
 */
const formattedTime = computed(() => {
  const options = {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  }
  const timeString = currentTime.value.toLocaleTimeString('en-US', options)
  const timezone = getTimezone()
  return `${timeString} (${timezone})`
})

/**
 * Update clock every second
 */
const updateClock = () => {
  currentTime.value = new Date()
}

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

/**
 * Initialize currency store and clock on mount
 */
onMounted(async () => {
  await currencyStore.initialize()
  updateClock()
  clockInterval = setInterval(updateClock, 1000)
})

/**
 * Cleanup clock interval
 */
onBeforeUnmount(() => {
  if (clockInterval) {
    clearInterval(clockInterval)
  }
})
</script>

<template>
  <div class="app-container">
    <!-- Sticky Top Bar -->
    <header class="top-bar" :class="{ 'full-width': !authStore.isAuthenticated }">
      <div class="top-bar-left">
        <CurrencySelector />
      </div>
      <div class="top-bar-right">
        <span class="clock-icon">🕐</span>
        <span class="clock-time">{{ formattedTime }}</span>
      </div>
    </header>

    <!-- Mobile Overlay (click to close menu) -->
    <div
      v-if="mobileMenuOpen"
      class="mobile-overlay"
      @click="closeMobileMenu"
    ></div>

    <!-- Side Navigation -->
    <aside v-if="authStore.isAuthenticated" class="sidebar" :class="{ 'mobile-open': mobileMenuOpen }">
      <!-- Sidebar Header with Logo -->
      <div class="sidebar-header">
        <RouterLink to="/" class="sidebar-logo" @click="closeMobileMenu">
          💰 Receipt Tracker
        </RouterLink>
      </div>

      <!-- Sidebar Navigation -->
      <nav class="sidebar-nav">
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
            <RouterLink to="/pending" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">✓</span>
              Validate Receipts
            </RouterLink>
            <RouterLink to="/transactions" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">📊</span>
              My Transactions
            </RouterLink>
          </div>

          <!-- Admin Section (only for System Admin) -->
          <div class="nav-section" v-if="authStore.user?.role === 'System Admin'">
            <div class="nav-section-title">Administration</div>
            <RouterLink to="/users" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">👥</span>
              User Management
            </RouterLink>
            <RouterLink to="/audit-logs" class="nav-item" @click="closeMobileMenu">
              <span class="nav-item-icon">📋</span>
              Audit Logs
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
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content" :class="{ 'no-sidebar': !authStore.isAuthenticated }">
      <!-- Mobile Menu Toggle -->
      <button
        v-if="authStore.isAuthenticated"
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

/* Sticky Top Bar */
.top-bar {
  position: fixed;
  top: 0;
  left: var(--sidebar-width);
  right: 0;
  height: 40px;
  background-color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary-dark);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-lg);
  z-index: 1050;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.top-bar.full-width {
  left: 0;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-white);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.clock-icon {
  font-size: 1.1em;
}

.clock-time {
  font-family: var(--font-family-mono);
  letter-spacing: 0.5px;
}

.top-bar-right {
  display: flex;
  align-items: center;
}

/* Adjust sidebar to account for top bar */
.sidebar {
  top: 0;
  height: 100vh;
}

/* Adjust main content to account for top bar */
.main-content {
  margin-top: 40px;
}

.main-content.no-sidebar {
  margin-left: 0;
}

/* Mobile Menu Toggle Button */
.mobile-menu-toggle {
  top: calc(40px + var(--spacing-md));

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

  .top-bar {
    left: 0;
    padding: 0 var(--spacing-sm);
  }

  .clock-time {
    font-size: 0.75rem;
  }

  .top-bar-left {
    gap: var(--spacing-xs);
  }
}
</style>
