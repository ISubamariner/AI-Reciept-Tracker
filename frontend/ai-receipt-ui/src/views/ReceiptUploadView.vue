<template>
  <div class="upload-container">
    <h2>AI Receipt Processor</h2>
    <p>Current Role: <strong>{{ authStore.currentUserRole }}</strong></p>

    <form @submit.prevent="handleUpload">
      <div class="form-group">
        <label for="imageUrl">Receipt Image URL</label>
        <input
          type="url"
          id="imageUrl"
          v-model="imageUrl"
          placeholder="e.g., https://myserver.com/receipt.jpg"
          required
        >
        <small class="hint">Note: In a real app, this would be a file upload to cloud storage (S3/R2).</small>
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Processing with Gemini...' : 'Analyze Receipt' }}
      </button>

      <p v-if="successMessage" class="success-message"> {{ successMessage }}</p>
      <p v-if="error" class="error-message"> {{ error }}</p>
    </form>

    <div v-if="extractedData" class="results-box">
      <h3>Extracted Transaction Data (Saved to DB)</h3>
      <pre>{{ JSON.stringify(extractedData, null, 2) }}</pre>
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

const handleUpload = async () => {
  isLoading.value = true;
  error.value = '';
  successMessage.value = '';
  extractedData.value = null;

  try {
    // 1. Call the dedicated service
    const result = await receiptService.uploadReceipt(imageUrl.value);

    successMessage.value = `Success! Transaction ID ${result.transaction_id} created.`;
    extractedData.value = result.extracted_data;

  } catch (err) {
    // 2. Display the role-based access error or general error
    error.value = err.message || 'An unknown error occurred during processing.';

  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.upload-container { max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; font-weight: bold; }
input { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.hint { font-size: 0.8em; color: #666; margin-top: 5px; }
button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; transition: background-color 0.3s; }
button:disabled { background-color: #a0c9f1; cursor: not-allowed; }
.success-message { color: green; font-weight: bold; margin-top: 15px; }
.error-message { color: red; font-weight: bold; margin-top: 15px; }
.results-box { margin-top: 25px; padding: 15px; background-color: #eee; border-radius: 4px; overflow-x: auto; }
pre { white-space: pre-wrap; word-wrap: break-word; font-size: 0.9em; }
</style>
