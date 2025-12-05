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
          <!-- Upload Mode Toggle -->
          <div class="form-group">
            <label class="form-label">Upload Method</label>
            <div class="d-flex gap-2">
              <label class="radio-label">
                <input type="radio" v-model="uploadMode" value="file" class="mr-1">
                📁 Upload File
              </label>
              <label class="radio-label">
                <input type="radio" v-model="uploadMode" value="url" class="mr-1">
                🔗 Image URL
              </label>
            </div>
          </div>

          <!-- File Upload Field -->
          <div v-if="uploadMode === 'file'" class="form-group">
            <label for="imageFile" class="form-label">📤 Select Receipt Image</label>
            <input
              type="file"
              id="imageFile"
              @change="handleFileSelect"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              class="form-input"
              required
            >
            <span class="form-hint">
              💡 Supported formats: PNG, JPEG, GIF, WebP (Max 16MB)
            </span>
            <!-- Preview -->
            <div v-if="imagePreview" class="mt-3">
              <img :src="imagePreview" alt="Receipt preview" style="max-width: 100%; max-height: 300px; border-radius: var(--border-radius); border: var(--border-width) solid var(--color-border);">
            </div>
          </div>

          <!-- Image URL Field -->
          <div v-if="uploadMode === 'url'" class="form-group">
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
              💡 Provide a publicly accessible image URL
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
          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="isLoading || (!selectedFile && uploadMode === 'file') || (!imageUrl && uploadMode === 'url')">
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

const uploadMode = ref('file'); // 'file' or 'url'
const imageUrl = ref('');
const selectedFile = ref(null);
const imagePreview = ref('');
const isLoading = ref(false);
const error = ref('');
const successMessage = ref('');
const extractedData = ref(null);

/**
 * Handle file selection and preview
 */
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

/**
 * Handle receipt upload and processing
 */
const handleUpload = async () => {
  isLoading.value = true;
  error.value = '';
  successMessage.value = '';
  extractedData.value = null;

  try {
    let result;
    if (uploadMode.value === 'file' && selectedFile.value) {
      result = await receiptService.uploadReceiptFile(selectedFile.value);
    } else if (uploadMode.value === 'url' && imageUrl.value) {
      result = await receiptService.uploadReceipt(imageUrl.value);
    } else {
      throw new Error('Please select a file or provide a URL');
    }

    successMessage.value = `Success! Transaction ID ${result.transaction_id} created.`;
    extractedData.value = result.extracted_data;

    // Clear form
    selectedFile.value = null;
    imagePreview.value = '';
    imageUrl.value = '';
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
