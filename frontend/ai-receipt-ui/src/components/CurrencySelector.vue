<!--
  CurrencySelector.vue - Currency Selection Dropdown Component

  A searchable dropdown for selecting a currency for viewing data.
  Features:
  - Searchable list of currencies
  - Displays currency code, name, and symbol
  - Persists selection to user preferences (if logged in)
  - Local storage fallback for non-authenticated users
-->

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCurrencyStore } from '@/stores/currency'
import { useAuthStore } from '@/stores/auth'

const currencyStore = useCurrencyStore()
const authStore = useAuthStore()

const isOpen = ref(false)
const searchQuery = ref('')
const savingPreference = ref(false)

// Filter currencies based on search query
const filteredCurrencies = computed(() => {
  if (!searchQuery.value) {
    return currencyStore.currencies
  }
  
  const query = searchQuery.value.toLowerCase()
  return currencyStore.currencies.filter(currency =>
    currency.code.toLowerCase().includes(query) ||
    currency.name.toLowerCase().includes(query) ||
    currency.symbol.includes(query)
  )
})

// Get current selected currency details
const selectedCurrency = computed(() => {
  return currencyStore.currentCurrency || { code: 'USD', name: 'US Dollar', symbol: '$' }
})

// Toggle dropdown
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
  }
}

// Close dropdown
const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
}

// Select a currency
const selectCurrency = async (currencyCode) => {
  try {
    // Update local selection
    currencyStore.setSelectedCurrency(currencyCode)
    
    // If user is logged in, save as preference
    if (authStore.isAuthenticated) {
      savingPreference.value = true
      try {
        await currencyStore.updateUserPreferredCurrency(currencyCode)
      } catch (error) {
        console.error('Failed to save currency preference:', error)
        // Continue anyway - local selection still works
      } finally {
        savingPreference.value = false
      }
    }
    
    closeDropdown()
  } catch (error) {
    console.error('Error selecting currency:', error)
  }
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.currency-selector')
  if (dropdown && !dropdown.contains(event.target)) {
    closeDropdown()
  }
}

// Initialize
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

// Cleanup
watch(() => isOpen.value, (newValue) => {
  if (!newValue) {
    searchQuery.value = ''
  }
})
</script>

<template>
  <div class="currency-selector">
    <!-- Selected Currency Display -->
    <button
      class="currency-button"
      @click="toggleDropdown"
      :disabled="currencyStore.loading"
      :aria-label="'Select currency, currently ' + selectedCurrency.code"
    >
      <span class="currency-symbol">{{ selectedCurrency.symbol }}</span>
      <span class="currency-code">{{ selectedCurrency.code }}</span>
      <span class="dropdown-arrow">{{ isOpen ? '▲' : '▼' }}</span>
    </button>

    <!-- Dropdown Menu -->
    <div v-if="isOpen" class="currency-dropdown">
      <!-- Search Input -->
      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search currencies..."
          class="search-input"
          @click.stop
          autofocus
        />
      </div>

      <!-- Currency List -->
      <div class="currency-list">
        <div
          v-for="currency in filteredCurrencies"
          :key="currency.code"
          class="currency-item"
          :class="{ active: currency.code === selectedCurrency.code }"
          @click="selectCurrency(currency.code)"
        >
          <span class="item-symbol">{{ currency.symbol }}</span>
          <div class="item-details">
            <div class="item-code">{{ currency.code }}</div>
            <div class="item-name">{{ currency.name }}</div>
          </div>
          <span v-if="currency.code === selectedCurrency.code" class="item-checkmark">✓</span>
        </div>

        <!-- No Results Message -->
        <div v-if="filteredCurrencies.length === 0" class="no-results">
          No currencies found matching "{{ searchQuery }}"
        </div>
      </div>

      <!-- Loading/Saving Indicator -->
      <div v-if="savingPreference" class="saving-indicator">
        Saving preference...
      </div>
    </div>
  </div>
</template>

<style scoped>
.currency-selector {
  position: relative;
  display: inline-block;
}

.currency-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: var(--color-white);
  color: var(--color-text-primary);
  border: 2px solid var(--color-secondary);
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  min-width: 120px;
}

.currency-button:hover {
  background-color: var(--color-secondary);
  border-color: var(--color-primary);
}

.currency-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.currency-symbol {
  font-size: 1.2em;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.currency-code {
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  font-size: 0.8em;
  opacity: 0.7;
}

.currency-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  width: 320px;
  max-height: 400px;
  background-color: var(--color-white);
  border: 2px solid var(--color-primary);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 1200;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-container {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(168, 220, 171, 0.2);
}

.currency-list {
  overflow-y: auto;
  max-height: 300px;
}

.currency-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color var(--transition-fast);
  border-bottom: 1px solid var(--color-border-light);
}

.currency-item:last-child {
  border-bottom: none;
}

.currency-item:hover {
  background-color: var(--color-secondary);
}

.currency-item.active {
  background-color: rgba(168, 220, 171, 0.2);
}

.item-symbol {
  font-size: 1.5em;
  font-weight: var(--font-weight-bold);
  min-width: 30px;
  text-align: center;
  color: var(--color-primary);
}

.item-details {
  flex: 1;
}

.item-code {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
}

.item-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: 0.125rem;
}

.item-checkmark {
  color: var(--color-success);
  font-size: 1.2em;
  font-weight: var(--font-weight-bold);
}

.no-results {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-md);
}

.saving-indicator {
  padding: 0.5rem;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-white);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .currency-dropdown {
    width: 280px;
    max-height: 350px;
  }

  .currency-button {
    min-width: 100px;
    padding: 0.4rem 0.75rem;
  }
}
</style>
