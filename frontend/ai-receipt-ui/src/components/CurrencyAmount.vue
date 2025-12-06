<!--
  CurrencyAmount.vue - Currency Display Component

  Displays an amount with automatic currency conversion.
  Shows original amount in a semi-transparent tag when converted.

  Props:
  - amount: The amount to display (number)
  - currency: The original currency code (string)
  - showOriginal: Whether to show the original amount tag (boolean, default: true)
  - size: Display size - 'sm', 'md', 'lg' (string, default: 'md')
-->

<script setup>
import { computed } from 'vue'
import { useCurrencyStore } from '@/stores/currency'

const props = defineProps({
  amount: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    required: true
  },
  showOriginal: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const currencyStore = useCurrencyStore()

// Check if conversion is needed
const needsConversion = computed(() => {
  return props.currency !== currencyStore.selectedCurrency
})

// Get converted amount
const convertedAmount = computed(() => {
  if (!needsConversion.value) {
    return props.amount
  }
  
  try {
    return currencyStore.convertAmountLocally(
      props.amount,
      props.currency,
      currencyStore.selectedCurrency
    )
  } catch (error) {
    console.error('Error converting amount:', error)
    return props.amount
  }
})

// Get display currency details
const displayCurrency = computed(() => {
  return currencyStore.getCurrencyByCode(currencyStore.selectedCurrency) || {
    code: currencyStore.selectedCurrency,
    symbol: '$'
  }
})

// Get original currency details
const originalCurrency = computed(() => {
  return currencyStore.getCurrencyByCode(props.currency) || {
    code: props.currency,
    symbol: '$'
  }
})

// Format amount with currency symbol
const formatAmount = (amount, currency) => {
  return `${currency.symbol}${amount.toFixed(2)}`
}
</script>

<template>
  <div class="currency-amount" :class="`size-${size}`">
    <!-- Main Amount Display -->
    <span class="main-amount">
      {{ formatAmount(convertedAmount, displayCurrency) }}
      <span class="currency-code">{{ displayCurrency.code }}</span>
    </span>

    <!-- Original Amount Tag (shown when converted) -->
    <span 
      v-if="needsConversion && showOriginal" 
      class="original-amount-tag"
      :title="`Original amount: ${formatAmount(amount, originalCurrency)} ${originalCurrency.code}`"
    >
      {{ formatAmount(amount, originalCurrency) }} {{ originalCurrency.code }}
    </span>
  </div>
</template>

<style scoped>
.currency-amount {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.main-amount {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
}

.currency-code {
  font-size: 0.85em;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-left: 0.25rem;
}

.original-amount-tag {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background-color: rgba(0, 0, 0, 0.1);
  color: var(--color-text-secondary);
  border-radius: var(--border-radius);
  font-size: 0.75em;
  font-weight: var(--font-weight-medium);
  opacity: 0.7;
  white-space: nowrap;
  cursor: help;
  transition: opacity var(--transition-fast);
}

.original-amount-tag:hover {
  opacity: 1;
}

/* Size Variants */
.size-sm .main-amount {
  font-size: var(--font-size-sm);
}

.size-sm .original-amount-tag {
  font-size: 0.7em;
  padding: 0.1rem 0.4rem;
}

.size-md .main-amount {
  font-size: var(--font-size-md);
}

.size-md .original-amount-tag {
  font-size: 0.75em;
}

.size-lg .main-amount {
  font-size: var(--font-size-lg);
}

.size-lg .original-amount-tag {
  font-size: 0.8em;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .original-amount-tag {
    background-color: rgba(255, 255, 255, 0.1);
  }
}
</style>
