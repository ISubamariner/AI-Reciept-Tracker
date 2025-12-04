<!--
  TransactionsView.vue - Transactions List Page

  Displays all user transactions with filtering and sorting.
  Uses fintech theme components for consistent styling.
-->

<template>
  <div class="content-body">
    <!-- Page Header -->
    <div class="card mb-4">
      <div class="card-header">
        <h2 class="card-title">📊 My Transactions</h2>
        <p class="card-subtitle">
          Logged in as: <strong>{{ authStore.currentUser }}</strong>
        </p>
      </div>
      <div class="card-body" v-if="!isLoading && transactions.length > 0">
        <div class="d-flex justify-between align-center">
          <div class="d-flex align-center gap-2">
            <span class="text-secondary">Total Transactions:</span>
            <span class="badge badge-info" style="font-size: var(--font-size-base);">{{ transactionCount }}</span>
          </div>
          <RouterLink to="/upload" class="btn btn-primary">
            📤 Upload New Receipt
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card text-center">
      <div class="card-body">
        <p class="text-secondary">🔄 Loading transactions...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card">
      <div class="card-body">
        <div class="alert alert-error mb-3">
          {{ error }}
        </div>
        <button @click="loadTransactions" class="btn btn-primary">
          🔄 Retry
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="transactions.length === 0" class="card text-center">
      <div class="card-body">
        <div style="font-size: 4rem; margin-bottom: var(--spacing-lg);">📥</div>
        <h3 class="mb-3">No Transactions Yet</h3>
        <p class="text-secondary mb-4">
          Upload your first receipt to get started tracking your expenses!
        </p>
        <RouterLink to="/upload" class="btn btn-primary btn-lg">
          📤 Upload Receipt
        </RouterLink>
      </div>
    </div>

    <!-- Transactions List -->
    <div v-else class="transactions-grid">
      <div class="card fade-in" v-for="txn in transactions" :key="txn.id">
        <div class="card-header">
          <div class="d-flex justify-between align-center">
            <h3 class="card-title" style="margin: 0;">
              {{ txn.vendor_name || 'Unknown Vendor' }}
            </h3>
            <span style="font-size: var(--font-size-xxl); font-weight: var(--font-weight-bold); color: var(--color-primary);">
              ${{ txn.total_amount.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="card-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">📅 Date</span>
              <span class="detail-value">{{ formatDate(txn.transaction_date) }}</span>
            </div>

            <div class="detail-item" v-if="txn.receipt_number">
              <span class="detail-label">📜 Receipt #</span>
              <span class="detail-value">{{ txn.receipt_number }}</span>
            </div>

            <div class="detail-item" v-if="txn.description">
              <span class="detail-label">📝 Description</span>
              <span class="detail-value">{{ txn.description }}</span>
            </div>

            <div class="detail-item">
              <span class="detail-label">🟢 Status</span>
              <span :class="getBadgeClass(txn.status)">{{ txn.status }}</span>
            </div>
          </div>
        </div>

        <div class="card-footer" v-if="txn.image_url">
          <a :href="txn.image_url" target="_blank" class="btn btn-outline btn-sm btn-block">
            🔍 View Receipt Image
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { receiptService } from '@/services/receiptService';

const authStore = useAuthStore();

const transactions = ref([]);
const transactionCount = ref(0);
const isLoading = ref(false);
const error = ref('');

/**
 * Load transactions from API
 */
const loadTransactions = async () => {
  isLoading.value = true;
  error.value = '';

  try {
    const result = await receiptService.getTransactions();
    transactions.value = result.transactions;
    transactionCount.value = result.count;
  } catch (err) {
    error.value = err.message || 'Failed to load transactions. Please try again.';
    console.error('Error loading transactions:', err);
  } finally {
    isLoading.value = false;
  }
};

/**
 * Format date for display
 */
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

/**
 * Get badge class based on status
 */
const getBadgeClass = (status) => {
  const statusLower = status?.toLowerCase() || '';
  if (statusLower === 'processed') return 'badge badge-success';
  if (statusLower === 'pending') return 'badge badge-warning';
  if (statusLower === 'error') return 'badge badge-error';
  return 'badge badge-info';
};

onMounted(() => {
  loadTransactions();
});
</script>

<style scoped>
/**
 * TransactionsView Custom Styles
 *
 * Component-specific styles that complement the base fintech theme.
 */

/* Transactions Grid Layout */
.transactions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
}

/* Detail Grid within Cards */
.detail-grid {
  display: grid;
  gap: var(--spacing-md);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.detail-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  text-align: right;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .transactions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
