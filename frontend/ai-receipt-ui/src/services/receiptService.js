import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL;

/**
 * Service to handle all API interactions related to receipts and transactions.
 */
export const receiptService = {
    /**
     * Calls the protected backend endpoint to process a receipt image URL.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @param {string} imageUrl - The public URL of the receipt image.
     * @returns {Promise<object>} The extracted data and transaction ID from the backend.
     */
    async uploadReceipt(imageUrl) {
        try {
            const response = await axios.post(`${API_URL}/receipts/upload`, {
                image_url: imageUrl
            });
            return response.data;
        } catch (error) {
            // Check for 403 (Forbidden - role mismatch) or other errors
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Uploads an image file to the backend for processing.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @param {File} file - The image file to upload.
     * @returns {Promise<object>} The extracted data and transaction ID from the backend.
     */
    async uploadReceiptFile(file) {
        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await axios.post(`${API_URL}/receipts/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            return response.data;
        } catch (error) {
            // Check for 403 (Forbidden - role mismatch) or other errors
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Fetches all transactions for the authenticated user.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @returns {Promise<object>} An object containing the transactions array and count.
     */
    async getTransactions() {
        try {
            const response = await axios.get(`${API_URL}/receipts/transactions`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                throw new Error("Unauthorized. Please log in again.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Fetches all pending receipts for the authenticated user.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @returns {Promise<object>} An object containing the pending receipts array and count.
     */
    async getPendingReceipts() {
        try {
            const response = await axios.get(`${API_URL}/receipts/pending`);
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                throw new Error("Unauthorized. Please log in again.");
            }
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Confirms a pending receipt and creates a transaction.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @param {object} confirmData - The confirmed receipt data with receipt_id and transaction details.
     * @returns {Promise<object>} The confirmation response with transaction ID.
     */
    async confirmReceipt(confirmData) {
        try {
            const response = await axios.post(`${API_URL}/receipts/confirm`, confirmData);
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                throw new Error("Unauthorized. Please log in again.");
            }
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Cancels a pending receipt.
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @param {number} receiptId - The ID of the receipt to cancel.
     * @returns {Promise<object>} The cancellation response.
     */
    async cancelReceipt(receiptId) {
        try {
            const response = await axios.post(`${API_URL}/receipts/cancel`, {
                receipt_id: receiptId
            });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                throw new Error("Unauthorized. Please log in again.");
            }
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    },

    /**
     * Rejects a pending receipt with an optional reason (e.g., duplicate).
     * The JWT token is automatically included via the Axios interceptor in auth.js.
     * @param {number} receiptId - The ID of the receipt to reject.
     * @param {string} reason - Optional reason for rejection (e.g., "Duplicate receipt").
     * @returns {Promise<object>} The rejection response.
     */
    async rejectReceipt(receiptId, reason = '') {
        try {
            const response = await axios.post(`${API_URL}/receipts/reject`, {
                receipt_id: receiptId,
                reason: reason
            });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                throw new Error("Unauthorized. Please log in again.");
            }
            if (error.response && error.response.status === 403) {
                throw new Error("Permission Denied. You must have a 'RECEIPT_LOGGER' or 'SYSTEM_ADMIN' role.");
            }
            throw error.response ? error.response.data : error;
        }
    }
};
