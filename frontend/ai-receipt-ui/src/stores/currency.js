import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL;

export const useCurrencyStore = defineStore('currency', {
    state: () => ({
        currencies: [],
        exchangeRates: {},
        selectedCurrency: localStorage.getItem('selectedCurrency') || 'USD',
        userPreferredCurrency: null,
        loading: false,
        error: null,
        lastUpdated: null,
    }),

    getters: {
        // Get currency details by code
        getCurrencyByCode: (state) => (code) => {
            return state.currencies.find(c => c.code === code);
        },

        // Get current selected currency details
        currentCurrency: (state) => {
            return state.currencies.find(c => c.code === state.selectedCurrency) || null;
        },

        // Get exchange rate for a specific currency
        getExchangeRate: (state) => (currencyCode) => {
            return state.exchangeRates[currencyCode]?.rate || null;
        },

        // Check if currencies are loaded
        isLoaded: (state) => state.currencies.length > 0,
    },

    actions: {
        // Fetch all available currencies
        async fetchCurrencies() {
            try {
                this.loading = true;
                this.error = null;

                const response = await axios.get(`${API_URL}/currency/currencies`);

                if (response.data.success) {
                    this.currencies = response.data.currencies;
                    return this.currencies;
                } else {
                    throw new Error(response.data.error || 'Failed to fetch currencies');
                }
            } catch (error) {
                // If it's a 503 (service unavailable), currency feature not set up yet
                if (error.response && error.response.status === 503) {
                    console.info('Currency feature not yet available. Run migration to enable.');
                    this.currencies = []; // Set empty array
                    return [];
                }
                this.error = error.message;
                console.error('Error fetching currencies:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // Fetch current exchange rates
        async fetchExchangeRates() {
            try {
                this.loading = true;
                this.error = null;

                const response = await axios.get(`${API_URL}/currency/exchange-rates`);

                if (response.data.success) {
                    this.exchangeRates = response.data.rates;
                    this.lastUpdated = new Date();
                    return this.exchangeRates;
                } else {
                    throw new Error(response.data.error || 'Failed to fetch exchange rates');
                }
            } catch (error) {
                // If it's a 503 (service unavailable), currency feature not set up yet
                if (error.response && error.response.status === 503) {
                    console.info('Currency feature not yet available. Run migration to enable.');
                    this.exchangeRates = {};
                    return {};
                }
                this.error = error.message;
                console.error('Error fetching exchange rates:', error);
                throw error;
            } finally {
                this.loading = false;
            }
        },

        // Convert an amount from one currency to another
        async convertCurrency(amount, fromCurrency, toCurrency) {
            try {
                const response = await axios.post(`${API_URL}/currency/convert`, {
                    amount,
                    from_currency: fromCurrency,
                    to_currency: toCurrency
                });

                if (response.data.success) {
                    return response.data;
                } else {
                    throw new Error(response.data.error || 'Conversion failed');
                }
            } catch (error) {
                console.error('Error converting currency:', error);
                throw error;
            }
        },

        // Convert amount using cached exchange rates (faster, but may be slightly outdated)
        convertAmountLocally(amount, fromCurrency, toCurrency) {
            if (fromCurrency === toCurrency) {
                return amount;
            }

            const fromRate = this.exchangeRates[fromCurrency]?.rate;
            const toRate = this.exchangeRates[toCurrency]?.rate;

            if (!fromRate || !toRate) {
                console.warn(`Exchange rate not found for ${fromCurrency} or ${toCurrency}`);
                return amount;
            }

            // Convert to USD first, then to target currency
            const amountInUSD = amount * fromRate.rate_to_usd;
            const convertedAmount = amountInUSD * toRate.rate_from_usd;

            return Math.round(convertedAmount * 100) / 100; // Round to 2 decimal places
        },

        // Set the selected currency for viewing
        setSelectedCurrency(currencyCode) {
            this.selectedCurrency = currencyCode;
            localStorage.setItem('selectedCurrency', currencyCode);
        },

        // Fetch user's preferred currency
        async fetchUserPreferredCurrency() {
            try {
                const response = await axios.get(`${API_URL}/currency/user/preferred-currency`);

                if (response.data.success) {
                    this.userPreferredCurrency = response.data.preferred_currency;
                    // Set as selected currency if not already set
                    if (!localStorage.getItem('selectedCurrency')) {
                        this.setSelectedCurrency(this.userPreferredCurrency);
                    }
                    return this.userPreferredCurrency;
                } else {
                    throw new Error(response.data.error || 'Failed to fetch preferred currency');
                }
            } catch (error) {
                console.error('Error fetching user preferred currency:', error);
                // Silently fail - user might not be logged in
                return null;
            }
        },

        // Update user's preferred currency
        async updateUserPreferredCurrency(currencyCode) {
            try {
                const response = await axios.put(`${API_URL}/currency/user/preferred-currency`, {
                    currency_code: currencyCode
                });

                if (response.data.success) {
                    this.userPreferredCurrency = currencyCode;
                    this.setSelectedCurrency(currencyCode);
                    return true;
                } else {
                    throw new Error(response.data.error || 'Failed to update preferred currency');
                }
            } catch (error) {
                console.error('Error updating user preferred currency:', error);
                throw error;
            }
        },

        // Initialize the currency store (call on app mount)
        async initialize() {
            try {
                // Fetch currencies and exchange rates in parallel (ignore 503 errors)
                await Promise.allSettled([
                    this.fetchCurrencies().catch(() => {}),
                    this.fetchExchangeRates().catch(() => {})
                ]);

                // Try to fetch user's preferred currency if logged in (ignore errors)
                await this.fetchUserPreferredCurrency().catch(() => {});

                return true;
            } catch (error) {
                // Silently fail - currency feature is optional
                console.info('Currency store initialization completed with limited features:', error.message);
                return false;
            }
        },

        // Format amount with currency symbol
        formatAmount(amount, currencyCode = null) {
            const currency = currencyCode 
                ? this.getCurrencyByCode(currencyCode)
                : this.currentCurrency;

            if (!currency) {
                return `$${amount.toFixed(2)}`;
            }

            return `${currency.symbol}${amount.toFixed(2)}`;
        },

        // Reset store
        reset() {
            this.currencies = [];
            this.exchangeRates = {};
            this.selectedCurrency = 'USD';
            this.userPreferredCurrency = null;
            this.loading = false;
            this.error = null;
            this.lastUpdated = null;
            localStorage.removeItem('selectedCurrency');
        }
    }
});
