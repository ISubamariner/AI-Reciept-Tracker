<template>
  <div class="pending-receipts-view">
    <div class="page-header">
      <h1>Validate Pending Receipts</h1>
      <p class="subtitle">Review and confirm AI-extracted receipt data</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading pending receipts...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-banner">
      <strong>Error:</strong> {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="pendingReceipts.length === 0" class="empty-state">
      <div class="empty-icon">✓</div>
      <h2>All Caught Up!</h2>
      <p>You have no pending receipts to validate.</p>
      <router-link to="/upload" class="btn btn-primary">Upload New Receipt</router-link>
    </div>

    <!-- Pending Receipts List -->
    <div v-else class="receipts-container">
      <div class="receipts-summary">
        <span class="count-badge">{{ pendingReceipts.length }}</span>
        <span>receipt{{ pendingReceipts.length !== 1 ? 's' : '' }} pending validation</span>
      </div>

      <div class="receipts-grid">
        <div
          v-for="receipt in pendingReceipts"
          :key="receipt.receipt_id"
          class="receipt-card"
          :class="{ 'editing': editingReceiptId === receipt.receipt_id }"
        >
          <!-- Receipt Header -->
          <div class="receipt-header">
            <div class="receipt-meta">
              <span class="receipt-id">Receipt #{{ receipt.receipt_id }}</span>
              <span class="receipt-date">{{ formatDate(receipt.timestamp) }}</span>
            </div>
            <span class="status-badge pending">Pending Validation</span>
          </div>

          <!-- Receipt Image Preview -->
          <div v-if="receipt.image_url" class="image-preview">
            <img
              :src="getImageUrl(receipt.image_url)"
              :alt="`Receipt ${receipt.receipt_id}`"
              @error="handleImageError"
            />
          </div>

          <!-- Extracted Data Form -->
          <form @submit.prevent="confirmReceipt(receipt)" class="receipt-form">
            <div class="form-group">
              <label for="vendor">Vendor Name</label>
              <input
                type="text"
                id="vendor"
                v-model="receipt.extracted_data.vendor_name"
                required
                :disabled="processingReceipts[receipt.receipt_id]"
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="amount">Total Amount</label>
                <input
                  type="number"
                  id="amount"
                  v-model.number="receipt.extracted_data.total_amount"
                  step="0.01"
                  required
                  :disabled="processingReceipts[receipt.receipt_id]"
                />
              </div>

              <div class="form-group">
                <label for="currency">Currency</label>
                <select
                  id="currency"
                  v-model="receipt.extracted_data.currency"
                  :disabled="processingReceipts[receipt.receipt_id]"
                >
                  <option v-for="curr in availableCurrencies" :key="curr.code" :value="curr.code">
                    {{ curr.code }} - {{ curr.name }} ({{ curr.symbol }})
                  </option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="date">Transaction Date</label>
                <input
                  type="date"
                  id="date"
                  v-model="receipt.extracted_data.transaction_date"
                  required
                  :disabled="processingReceipts[receipt.receipt_id]"
                />
              </div>

              <div class="form-group">
                <label for="receipt-number">Receipt Number</label>
                <input
                  type="text"
                  id="receipt-number"
                  v-model="receipt.extracted_data.receipt_number"
                  :disabled="processingReceipts[receipt.receipt_id]"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="payer">Payer Name</label>
              <input
                type="text"
                id="payer"
                v-model="receipt.extracted_data.payer_name"
                :disabled="processingReceipts[receipt.receipt_id]"
              />
            </div>

            <!-- Action Buttons -->
            <div class="form-actions">
              <button
                type="submit"
                class="btn btn-success"
                :disabled="processingReceipts[receipt.receipt_id]"
              >
                <span v-if="processingReceipts[receipt.receipt_id]">Confirming...</span>
                <span v-else>✓ Confirm & Save</span>
              </button>

              <button
                type="button"
                class="btn btn-warning"
                @click="showRejectModal(receipt.receipt_id)"
                :disabled="processingReceipts[receipt.receipt_id]"
              >
                <span v-if="processingReceipts[receipt.receipt_id]">Processing...</span>
                <span v-else>⚠ Reject</span>
              </button>

              <button
                type="button"
                class="btn btn-danger"
                @click="cancelReceipt(receipt.receipt_id)"
                :disabled="processingReceipts[receipt.receipt_id]"
              >
                <span v-if="processingReceipts[receipt.receipt_id]">Processing...</span>
                <span v-else>✗ Cancel</span>
              </button>
            </div>
          </form>

          <!-- Processing Overlay -->
          <div v-if="processingReceipts[receipt.receipt_id]" class="processing-overlay">
            <div class="spinner"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div v-if="successMessage" class="toast toast-success">
      {{ successMessage }}
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModalFlag" class="modal-overlay" @click="closeRejectModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Reject Receipt</h2>
          <button class="modal-close" @click="closeRejectModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>Please provide a reason for rejecting this receipt:</p>
          <select v-model="rejectReason" class="reject-reason-select">
            <option value="">Select a reason...</option>
            <option value="Duplicate receipt">Duplicate receipt</option>
            <option value="Poor image quality">Poor image quality</option>
            <option value="Wrong receipt uploaded">Wrong receipt uploaded</option>
            <option value="Personal expense (not business)">Personal expense (not business)</option>
            <option value="Already processed manually">Already processed manually</option>
            <option value="Other">Other</option>
          </select>
          <textarea
            v-if="rejectReason === 'Other' || rejectReason"
            v-model="rejectReasonCustom"
            class="reject-reason-textarea"
            :placeholder="rejectReason === 'Other' ? 'Please specify the reason...' : 'Add additional notes (optional)'"
            rows="3"
          ></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeRejectModal">Cancel</button>
          <button
            class="btn btn-warning"
            @click="confirmReject"
            :disabled="!rejectReason"
          >
            Reject Receipt
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { receiptService } from '../services/receiptService';
import { useCurrencyStore } from '@/stores/currency';

export default {
  name: 'PendingReceiptsView',

  setup() {
    const currencyStore = useCurrencyStore();
    const pendingReceipts = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const editingReceiptId = ref(null);
    const processingReceipts = ref({});
    const successMessage = ref('');
    const showRejectModalFlag = ref(false);
    const rejectingReceiptId = ref(null);
    const rejectReason = ref('');
    const rejectReasonCustom = ref('');

    // Get available currencies from the store
    const availableCurrencies = computed(() => currencyStore.currencies);

    const loadPendingReceipts = async () => {
      loading.value = true;
      error.value = null;

      try {
        const data = await receiptService.getPendingReceipts();
        pendingReceipts.value = data.pending_receipts || [];
      } catch (err) {
        error.value = err.message || 'Failed to load pending receipts.';
        console.error('Error loading pending receipts:', err);
      } finally {
        loading.value = false;
      }
    };

    const confirmReceipt = async (receipt) => {
      const receiptId = receipt.receipt_id;
      processingReceipts.value[receiptId] = true;
      error.value = null;

      try {
        const confirmData = {
          receipt_id: receiptId,
          vendor_name: receipt.extracted_data.vendor_name,
          receipt_number: receipt.extracted_data.receipt_number,
          total_amount: receipt.extracted_data.total_amount,
          currency: receipt.extracted_data.currency,
          transaction_date: receipt.extracted_data.transaction_date,
          payer_name: receipt.extracted_data.payer_name
        };

        await receiptService.confirmReceipt(confirmData);

        // Remove from pending list
        pendingReceipts.value = pendingReceipts.value.filter(
          r => r.receipt_id !== receiptId
        );

        // Show success message
        showSuccessMessage(`Receipt #${receiptId} confirmed successfully!`);

      } catch (err) {
        error.value = err.message || 'Failed to confirm receipt.';
        console.error('Error confirming receipt:', err);
      } finally {
        processingReceipts.value[receiptId] = false;
      }
    };

    const cancelReceipt = async (receiptId) => {
      if (!confirm('Are you sure you want to cancel this receipt? This cannot be undone.')) {
        return;
      }

      processingReceipts.value[receiptId] = true;
      error.value = null;

      try {
        await receiptService.cancelReceipt(receiptId);

        // Remove from pending list
        pendingReceipts.value = pendingReceipts.value.filter(
          r => r.receipt_id !== receiptId
        );

        // Show success message
        showSuccessMessage(`Receipt #${receiptId} cancelled.`);

      } catch (err) {
        error.value = err.message || 'Failed to cancel receipt.';
        console.error('Error cancelling receipt:', err);
      } finally {
        processingReceipts.value[receiptId] = false;
      }
    };

    const showSuccessMessage = (message) => {
      successMessage.value = message;
      setTimeout(() => {
        successMessage.value = '';
      }, 3000);
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const getImageUrl = (imageUrl) => {
      // Handle different image URL formats
      if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
        return imageUrl;
      }
      if (imageUrl.startsWith('uploaded://')) {
        // Construct the correct backend URL for uploaded files
        const filename = imageUrl.replace('uploaded://', '');
        return `${import.meta.env.VITE_API_BASE_URL}/receipts/uploads/${filename}`;
      }
      return imageUrl;
    };

    const handleImageError = (event) => {
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect fill="%23ddd" width="200" height="150"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage Not Available%3C/text%3E%3C/svg%3E';
    };

    const showRejectModal = (receiptId) => {
      rejectingReceiptId.value = receiptId;
      showRejectModalFlag.value = true;
      rejectReason.value = '';
      rejectReasonCustom.value = '';
    };

    const closeRejectModal = () => {
      showRejectModalFlag.value = false;
      rejectingReceiptId.value = null;
      rejectReason.value = '';
      rejectReasonCustom.value = '';
    };

    const confirmReject = async () => {
      const receiptId = rejectingReceiptId.value;
      if (!receiptId) return;

      processingReceipts.value[receiptId] = true;
      error.value = null;

      try {
        // Build the full reason
        let fullReason = rejectReason.value;
        if (rejectReasonCustom.value) {
          fullReason = rejectReason.value === 'Other'
            ? rejectReasonCustom.value
            : `${rejectReason.value} - ${rejectReasonCustom.value}`;
        }

        await receiptService.rejectReceipt(receiptId, fullReason);

        // Remove from pending list
        pendingReceipts.value = pendingReceipts.value.filter(
          r => r.receipt_id !== receiptId
        );

        // Close modal and show success message
        closeRejectModal();
        showSuccessMessage(`Receipt #${receiptId} rejected: ${fullReason}`);

      } catch (err) {
        error.value = err.message || 'Failed to reject receipt.';
        console.error('Error rejecting receipt:', err);
        closeRejectModal();
      } finally {
        processingReceipts.value[receiptId] = false;
      }
    };

    onMounted(() => {
      loadPendingReceipts();
    });

    return {
      pendingReceipts,
      loading,
      error,
      editingReceiptId,
      processingReceipts,
      successMessage,
      showRejectModalFlag,
      rejectReason,
      rejectReasonCustom,
      availableCurrencies,
      confirmReceipt,
      cancelReceipt,
      showRejectModal,
      closeRejectModal,
      confirmReject,
      formatDate,
      getImageUrl,
      handleImageError
    };
  }
};
</script>

<style scoped>
.pending-receipts-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1.1rem;
}

/* Loading State */
.loading-container {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error Banner */
.error-banner {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: var(--color-success);
  margin-bottom: 1rem;
}

.empty-state h2 {
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
}

/* Receipts Summary */
.receipts-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: var(--color-text);
}

.count-badge {
  background-color: var(--color-warning);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: bold;
}

/* Receipts Grid */
.receipts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 2rem;
}

.receipt-card {
  background: white;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
  transition: all 0.3s ease;
}

.receipt-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.receipt-card.editing {
  border-color: var(--color-primary);
}

/* Receipt Header */
.receipt-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--color-border);
}

.receipt-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.receipt-id {
  font-weight: bold;
  color: var(--color-heading);
  font-size: 1.1rem;
}

.receipt-date {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

/* Image Preview */
.image-preview {
  margin-bottom: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f5f5f5;
  max-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

/* Receipt Form */
.receipt-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-group input:disabled,
.form-group select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  flex: 1 1 auto;
  min-width: 120px;
  padding: 0.875rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success {
  background-color: var(--color-success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #28a745;
  transform: translateY(-1px);
}

.btn-warning {
  background-color: var(--color-warning);
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
  transform: translateY(-1px);
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  display: inline-block;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
}

/* Processing Overlay */
.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

/* Success Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.toast-success {
  background-color: var(--color-success);
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  color: var(--color-heading);
  font-size: 1.5rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: #f0f0f0;
  color: var(--color-danger);
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin: 0 0 1rem;
  color: var(--color-text);
}

.reject-reason-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.reject-reason-select:focus {
  outline: none;
  border-color: var(--color-warning);
}

.reject-reason-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.reject-reason-textarea:focus {
  outline: none;
  border-color: var(--color-warning);
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 2px solid var(--color-border);
  justify-content: flex-end;
}

.modal-footer .btn {
  flex: 0 1 auto;
  min-width: 120px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .receipts-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .pending-receipts-view {
    padding: 1rem;
  }

  .modal-content {
    width: 95%;
  }
}
</style>
