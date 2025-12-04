<!--
  ReceiptUploadView.vue - Receipt Upload & Processing Page

  Allows users to upload receipt images for AI processing.
  Uses fintech theme components for consistent styling.
-->

<template>
  <div class="content-body">
    <!-- Page Header -->
    <div class="card mb-4">
      <div class="card-header">
        <h2 class="card-title">📤 AI Receipt Processor</h2>
        <p class="card-subtitle">
          Upload your receipt and let AI extract transaction details
        </p>
      </div>
      <div class="card-body">
        <div class="d-flex align-center gap-2">
          <span class="text-secondary">Current Role:</span>
          <span class="badge badge-info">{{ authStore.currentUserRole }}</span>
        </div>
      </div>
    </div>

    <!-- Upload Form Card -->
    <div class="card mb-4">
      <div class="card-body">
        <form @submit.prevent="handleUpload">
          <!-- Image URL Field -->
          <div class="form-group">
            <label for="imageUrl" class="form-label">📎 Receipt Image URL</label>
            <input
              type="url"
              id="imageUrl"
              v-model="imageUrl"
              class="form-input"
              placeholder="e.g., https://myserver.com/receipt.jpg"
              required
            >
            <span class="form-hint">
              💡 Note: In a production app, this would be a file upload to cloud storage (S3/R2).
            </span>
          </div>

          <!-- Success Alert -->
          <div v-if="successMessage" class="alert alert-success">
            ✓ {{ successMessage }}
          </div>

          <!-- Error Alert -->
          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="isLoading">
            {{ isLoading ? '🔄 Processing with AI...' : '🤖 Analyze Receipt' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Results Card -->
    <div v-if="extractedData" class="card fade-in">
      <div class="card-header">
        <h3 class="card-title">📊 Extracted Transaction Data</h3>
        <p class="card-subtitle">Successfully saved to database</p>
      </div>
      <div class="card-body">
        <div class="table-container">
          <table class="table">
            <tbody>
              <tr v-for="(value, key) in extractedData" :key="key">
                <td style="font-weight: var(--font-weight-semibold); text-transform: capitalize;">
                  {{ formatKey(key) }}
                </td>
                <td>{{ formatValue(value) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Raw JSON (collapsible) -->
        <details class="mt-3">
          <summary style="cursor: pointer; font-weight: var(--font-weight-semibold); color: var(--color-primary);">
            View Raw JSON
          </summary>
          <pre style="margin-top: var(--spacing-md); padding: var(--spacing-md); background-color: var(--color-background-alt); border: var(--border-width) solid var(--color-border); border-radius: var(--border-radius); overflow-x: auto; font-family: var(--font-family-mono); font-size: var(--font-size-sm);">{{ JSON.stringify(extractedData, null, 2) }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { receiptService } from '@/services/receiptService';

const authStore = useAuthStore();

const imageUrl = ref('');
const isLoading = ref(false);
const error = ref('');
const successMessage = ref('');
const extractedData = ref(null);

/**
 * Handle receipt upload and processing
 */
const handleUpload = async () => {
  isLoading.value = true;
  error.value = '';
  successMessage.value = '';
  extractedData.value = null;

  try {
    const result = await receiptService.uploadReceipt(imageUrl.value);
    successMessage.value = `Success! Transaction ID ${result.transaction_id} created.`;
    extractedData.value = result.extracted_data;
  } catch (err) {
    error.value = err.message || 'An unknown error occurred during processing.';
  } finally {
    isLoading.value = false;
  }
};

/**
 * Format object keys for display
 */
const formatKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Format values for display
 */
const formatValue = (value) => {
  if (value === null || value === undefined) return 'N/A';
  if (typeof value === 'object') return JSON.stringify(value);
  return value;
};
</script>
