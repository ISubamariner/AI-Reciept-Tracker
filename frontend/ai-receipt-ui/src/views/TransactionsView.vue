<template>
  <div class="transactions-container">
    <h2>My Transactions</h2>
    <p class="user-info">Logged in as: <strong>{{ authStore.currentUser }}</strong></p>

    <div v-if="isLoading" class="loading">
      <p>Loading transactions...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadTransactions">Retry</button>
    </div>

    <div v-else-if="transactions.length === 0" class="no-transactions">
      <p>No transactions found. Upload a receipt to get started!</p>
      <RouterLink to="/upload" class="upload-link">Upload Receipt</RouterLink>
    </div>

    <div v-else class="transactions-list">
      <p class="count">Total Transactions: <strong>{{ transactionCount }}</strong></p>

      <div class="transaction-card" v-for="txn in transactions" :key="txn.id">
        <div class="transaction-header">
          <h3>{{ txn.vendor_name || 'Unknown Vendor' }}</h3>
          <span class="amount">${{ txn.total_amount.toFixed(2) }}</span>
        </div>

        <div class="transaction-details">
          <div class="detail-row">
            <span class="label">Date:</span>
            <span class="value">{{ formatDate(txn.transaction_date) }}</span>
          </div>

          <div class="detail-row" v-if="txn.receipt_number">
            <span class="label">Receipt #:</span>
            <span class="value">{{ txn.receipt_number }}</span>
          </div>

          <div class="detail-row" v-if="txn.description">
            <span class="label">Description:</span>
            <span class="value">{{ txn.description }}</span>
          </div>

          <div class="detail-row">
            <span class="label">Status:</span>
            <span class="value status" :class="txn.status?.toLowerCase()">{{ txn.status }}</span>
          </div>
        </div>

        <div class="transaction-footer" v-if="txn.image_url">
          <a :href="txn.image_url" target="_blank" class="view-receipt">View Receipt Image</a>
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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

onMounted(() => {
  loadTransactions();
});
</script>

<style scoped>
.transactions-container {
  max-width: 900px;
  margin: 30px auto;
  padding: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.user-info {
  color: #666;
  margin-bottom: 30px;
  font-size: 0.95em;
}

.loading, .no-transactions {
  text-align: center;
  padding: 40px;
  color: #666;
}

.upload-link {
  display: inline-block;
  margin-top: 15px;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.upload-link:hover {
  background-color: #0056b3;
}

.error-message {
  text-align: center;
  padding: 20px;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c00;
}

.error-message button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.count {
  margin-bottom: 20px;
  font-size: 1.1em;
  color: #555;
}

.transactions-list {
  margin-top: 20px;
}

.transaction-card {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s;
}

.transaction-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.transaction-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3em;
}

.amount {
  font-size: 1.5em;
  font-weight: bold;
  color: #28a745;
}

.transaction-details {
  margin-bottom: 15px;
}

.detail-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #555;
  min-width: 120px;
}

.value {
  color: #333;
  flex: 1;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
  text-transform: uppercase;
}

.status.processed {
  background-color: #d4edda;
  color: #155724;
}

.status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status.error {
  background-color: #f8d7da;
  color: #721c24;
}

.transaction-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.view-receipt {
  display: inline-block;
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.view-receipt:hover {
  color: #0056b3;
  text-decoration: underline;
}
</style>
