# Multi-Currency System Documentation

## Overview

The Receipt Tracker now supports multiple currencies with automatic conversion and exchange rate management. The system uses USD as the base currency and provides real-time currency conversion for viewing data in any supported currency.

## Features

### 1. Currency Catalog
- **24 supported currencies** including:
  - USD (United States Dollar)
  - EUR (Euro)
  - GBP (British Pound)
  - PHP (Philippine Peso) ⭐
  - JPY (Japanese Yen)
  - CNY (Chinese Yuan)
  - And 18 more...

### 2. Automatic Exchange Rate Updates
- Exchange rates update **every 12 hours** automatically
- Uses exchangerate-api.com for accurate rates
- Rates are stored in the database for historical tracking
- Manual update available for System Admins

### 3. Multi-Currency Receipt Storage
- Receipts can be in any supported currency
- Original currency and amount are preserved
- Automatic conversion to USD (base currency) for consistent storage
- Exchange rate used for conversion is recorded

### 4. Flexible Currency Display
- **Searchable dropdown** in the navigation bar
- View all data in your preferred currency
- Shows original amount in a semi-transparent tag when converted
- Example: `₱500.00 PHP` shows with tag `$9.01 USD` if viewing in PHP

### 5. User Preferences
- Logged-in users can save their preferred currency
- Preference persists across sessions
- Synced to the database
- Guest users have local storage fallback

### 6. Data Validation
- Prevents duplicate exchange rates
- Validates currency codes against the catalog
- Ensures data consistency across the system

---

## Backend Implementation

### Database Models

#### Currency Model
```python
class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True)  # ISO 4217
    name = db.Column(db.String(64))
    symbol = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
```

#### ExchangeRate Model
```python
class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(3))
    rate_to_usd = db.Column(db.Numeric(20, 10))    # Foreign to USD
    rate_from_usd = db.Column(db.Numeric(20, 10))  # USD to Foreign
    timestamp = db.Column(db.DateTime)
    source = db.Column(db.String(64))
```

#### Updated Transaction Model
```python
class Transaction(db.Model):
    # Original receipt data
    original_amount = db.Column(db.Numeric(10, 2))
    original_currency = db.Column(db.String(3))
    
    # Converted to USD (base currency)
    total_amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10), default='USD')
    exchange_rate_used = db.Column(db.Numeric(20, 10))
```

#### Updated User Model
```python
class User(db.Model):
    preferred_currency = db.Column(db.String(3), default='USD')
```

### Services

#### CurrencyService (`app/services/currency_service.py`)
- `initialize_currencies()` - Load currency catalog
- `get_all_currencies()` - Fetch available currencies
- `fetch_exchange_rates_from_api()` - Get rates from external API
- `update_exchange_rates()` - Update rates in database
- `get_latest_rate(code)` - Get most recent rate for a currency
- `convert_amount(amount, from_currency, to_currency)` - Convert between currencies
- `should_update_rates()` - Check if update is needed

#### SchedulerService (`app/services/scheduler_service.py`)
- Automatic exchange rate updates every 12 hours
- Uses APScheduler for background task scheduling
- Manual trigger available via API endpoint

### API Endpoints

#### Currency Endpoints (`/api/currency/...`)

**Get All Currencies**
```
GET /api/currency/currencies
Response: {
  "success": true,
  "currencies": [
    {
      "id": 1,
      "code": "USD",
      "name": "United States Dollar",
      "symbol": "$",
      "is_active": true
    },
    ...
  ]
}
```

**Get Exchange Rates**
```
GET /api/currency/exchange-rates
Response: {
  "success": true,
  "base_currency": "USD",
  "rates": {
    "PHP": {
      "currency": {...},
      "rate": {
        "rate_to_usd": 0.0180,
        "rate_from_usd": 55.50,
        "timestamp": "2024-12-05T10:00:00"
      }
    },
    ...
  }
}
```

**Convert Currency**
```
POST /api/currency/convert
Body: {
  "amount": 100,
  "from_currency": "PHP",
  "to_currency": "USD"
}
Response: {
  "success": true,
  "original_amount": 100,
  "original_currency": "PHP",
  "converted_amount": 1.80,
  "target_currency": "USD",
  "rate_used": 0.0180
}
```

**Get User Preferred Currency** (Requires Auth)
```
GET /api/currency/user/preferred-currency
Response: {
  "success": true,
  "preferred_currency": "PHP",
  "currency_details": {...}
}
```

**Update User Preferred Currency** (Requires Auth)
```
PUT /api/currency/user/preferred-currency
Body: {
  "currency_code": "PHP"
}
Response: {
  "success": true,
  "message": "Preferred currency updated successfully"
}
```

**Trigger Manual Exchange Rate Update** (System Admin Only)
```
POST /api/currency/exchange-rates/update
Response: {
  "success": true,
  "message": "Exchange rate update triggered successfully",
  "updated": true
}
```

---

## Frontend Implementation

### Stores

#### Currency Store (`src/stores/currency.js`)

**State:**
- `currencies` - Array of available currencies
- `exchangeRates` - Object mapping currency codes to rates
- `selectedCurrency` - Currently selected display currency
- `userPreferredCurrency` - User's saved preference

**Key Methods:**
- `fetchCurrencies()` - Load currency catalog
- `fetchExchangeRates()` - Load current rates
- `convertAmountLocally(amount, from, to)` - Quick conversion using cached rates
- `setSelectedCurrency(code)` - Change display currency
- `updateUserPreferredCurrency(code)` - Save user preference
- `initialize()` - Setup on app load

### Components

#### CurrencySelector (`src/components/CurrencySelector.vue`)
- Searchable dropdown for currency selection
- Shows currency code, name, and symbol
- Saves to user preferences when logged in
- Falls back to localStorage for guests
- Located in the navigation sidebar

#### CurrencyAmount (`src/components/CurrencyAmount.vue`)
- Displays amounts with automatic conversion
- Props:
  - `amount` (Number) - The amount to display
  - `currency` (String) - Original currency code
  - `showOriginal` (Boolean) - Show original amount tag
  - `size` ('sm'|'md'|'lg') - Display size
- Shows original amount in semi-transparent tag when converted

**Usage Example:**
```vue
<CurrencyAmount 
  :amount="500" 
  currency="PHP"
  size="lg"
/>
```

**Output (when viewing in USD):**
```
$9.01 USD [₱500.00 PHP]
```

### Updated Views

#### TransactionsView
- Uses `CurrencyAmount` component for transaction display
- Shows amounts in selected currency with original amount tag

#### PendingReceiptsView
- Currency dropdown populated from currency store
- Supports all 24 currencies in receipt validation

---

## Database Migration

Run the migration script to add currency system tables:

```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Navigate to backend directory
cd portfolio-ai-app\backend-api

# Install new dependency
pip install APScheduler==3.10.4

# Run migration
python migrate_add_currency_system.py
```

The migration will:
1. Create `currencies` table
2. Create `exchange_rates` table
3. Add `preferred_currency` column to `users` table
4. Add currency columns to `transactions` table
5. Initialize currency catalog
6. Fetch initial exchange rates

---

## Usage Guide

### For Users

1. **Select Your Preferred Currency**
   - Look for the currency selector in the navigation sidebar
   - Search or scroll to find your currency (e.g., "PHP" or "Philippine Peso")
   - Click to select
   - Your choice is automatically saved

2. **Upload Receipts in Any Currency**
   - Upload receipt as usual
   - When validating, select the currency from the dropdown
   - System automatically converts to USD for storage

3. **View Transactions**
   - All amounts display in your selected currency
   - Original amounts shown in small gray tags
   - Hover over tags to see full details

### For Developers

1. **Add a New Currency**
   - Edit `CURRENCY_CATALOG` in `currency_service.py`
   - Run currency initialization
   - Exchange rates will be fetched automatically

2. **Use Currency Conversion**
   ```python
   from app.services.currency_service import CurrencyService
   
   converted, rate, timestamp = CurrencyService.convert_amount(
       100.0,
       'PHP',
       'USD'
   )
   ```

3. **Display Currency Amounts in Vue**
   ```vue
   <CurrencyAmount 
     :amount="transaction.original_amount" 
     :currency="transaction.original_currency"
   />
   ```

### For Administrators

1. **Manual Exchange Rate Update**
   - Only System Admins can trigger manual updates
   - Use the API endpoint or admin panel (when implemented)
   - Rates update automatically every 12 hours

2. **Monitor Exchange Rates**
   - Check database for recent rates
   - View rate history and trends
   - Identify currencies needing attention

---

## Technical Details

### Exchange Rate Flow

1. **Automatic Updates (Every 12 Hours)**
   ```
   Scheduler → CurrencyService.update_exchange_rates()
   → Fetch from API → Validate → Store in DB
   ```

2. **Receipt Processing**
   ```
   User uploads receipt (PHP 500)
   → User confirms with currency
   → Convert to USD (500 × 0.018 = $9.00)
   → Store both amounts + rate used
   ```

3. **Display Conversion**
   ```
   Load transaction ($9.00 USD, originally 500 PHP)
   → User viewing in EUR
   → Convert: $9.00 → €8.25
   → Display: €8.25 EUR [₱500.00 PHP]
   ```

### Data Validation

- **Unique Constraints:** Prevents duplicate currency codes
- **Timestamp Checks:** Avoids redundant rate updates within 11 hours
- **Foreign Keys:** Ensures referential integrity
- **Active Status:** Supports disabling currencies without deletion

### Error Handling

- **API Failures:** Logs warning, continues with cached rates
- **Conversion Errors:** Falls back to original amount
- **Missing Rates:** Returns error message to user
- **Invalid Currencies:** Rejects at API level

---

## Troubleshooting

### Exchange Rates Not Updating

1. Check scheduler status in logs
2. Verify internet connectivity
3. Check API rate limits (1500 requests/month free tier)
4. Manually trigger update as System Admin

### Currency Not Appearing in Dropdown

1. Verify currency exists in database
2. Check `is_active` flag
3. Refresh frontend currency store

### Conversion Showing Incorrect Amounts

1. Check if exchange rates are recent
2. Verify rate calculation logic
3. Check for rounding issues

### User Preference Not Saving

1. Verify user is logged in
2. Check authentication token
3. Verify database connection

---

## Future Enhancements

- [ ] Historical exchange rate charts
- [ ] Multi-currency transaction reports
- [ ] Cryptocurrency support
- [ ] Custom exchange rates for specific transactions
- [ ] Bulk currency conversion tool
- [ ] Exchange rate alerts/notifications
- [ ] PDF export with currency details

---

## Dependencies

### Backend
- `APScheduler==3.10.4` - Task scheduling
- `requests` - API calls (already installed)
- `SQLAlchemy` - Database ORM (already installed)

### Frontend
- No new dependencies required
- Uses existing Pinia and Axios

---

## API Rate Limits

**exchangerate-api.com** (Free Tier):
- 1,500 requests per month
- Updates every 12 hours = ~60 requests/month
- Plenty of headroom for manual updates and development

**To upgrade:**
- Pro plan: $12/month for 100,000 requests
- Not needed for typical usage

---

## Support

For questions or issues:
1. Check this documentation
2. Review code comments in service files
3. Check application logs
4. Contact system administrator

---

**Version:** 1.0.0  
**Last Updated:** December 5, 2024  
**Author:** AI Receipt Tracker Team
