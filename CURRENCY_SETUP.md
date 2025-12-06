# Quick Setup: Multi-Currency System

## Prerequisites
- Backend and frontend already running
- PostgreSQL database connected
- MongoDB connected

## Installation Steps

### 1. Install Backend Dependencies

```powershell
# Navigate to backend directory
cd portfolio-ai-app\backend-api

# Activate virtual environment (if not already active)
& ..\..\..\.venv\Scripts\Activate.ps1

# Install new dependency
pip install APScheduler==3.10.4
```

### 2. Run Database Migration

```powershell
# Still in backend-api directory
python migrate_add_currency_system.py
```

Expected output:
```
Starting currency system migration...
Step 1: Creating new tables...
✓ 'currencies' table created
✓ 'exchange_rates' table created
Step 2: Adding new columns...
✓ Added 'preferred_currency' column
✓ Added 'original_currency' column
✓ Added 'original_amount' column
Step 3: Initializing currency catalog...
✓ Initialized 24 currencies
Step 4: Fetching initial exchange rates...
✓ Successfully fetched initial exchange rates
Migration completed successfully!
```

### 3. Restart Backend Server

```powershell
# Stop current server (Ctrl+C)
# Restart
python run.py
```

The scheduler will initialize automatically and update exchange rates every 12 hours.

### 4. Frontend - No Changes Needed!

The frontend will automatically load:
- Currency store on app mount
- Available currencies from API
- Current exchange rates
- Currency selector component in navbar

## Verification

### Test Backend

1. **Check currencies endpoint:**
   ```
   GET http://localhost:5000/api/currency/currencies
   ```

2. **Check exchange rates:**
   ```
   GET http://localhost:5000/api/currency/exchange-rates
   ```

3. **Test conversion:**
   ```
   POST http://localhost:5000/api/currency/convert
   Body: {
     "amount": 100,
     "from_currency": "PHP",
     "to_currency": "USD"
   }
   ```

### Test Frontend

1. Open the app in your browser
2. Login to your account
3. Look for the currency selector in the left sidebar (bottom section)
4. Click it to see the searchable currency list
5. Select "PHP - Philippine Peso (₱)"
6. Navigate to transactions - amounts should now show in PHP

## Quick Feature Test

1. **Upload a receipt with PHP currency:**
   - Go to Upload Receipt
   - Upload an image
   - In validation, select "PHP" from currency dropdown
   - Enter amount (e.g., 500)
   - Confirm

2. **View in different currencies:**
   - Go to My Transactions
   - Change currency selector to USD
   - See conversion with original PHP amount in gray tag
   - Change to EUR
   - See amounts convert again

3. **Check persistence:**
   - Logout
   - Login again
   - Currency preference should be remembered

## Troubleshooting

### Migration fails
- Check PostgreSQL connection
- Verify database credentials in `.env`
- Ensure no conflicting table names

### Exchange rates not fetching
- Check internet connection
- Verify API access: https://api.exchangerate-api.com/v4/latest/USD
- Check logs for errors

### Currency selector not showing
- Check browser console for errors
- Verify frontend dev server is running
- Clear browser cache and reload

### Amounts not converting
- Verify exchange rates exist in database
- Check that currency store initialized
- Look for conversion errors in browser console

## Environment Variables

No new environment variables needed! The system uses:
- Existing database connection
- Public API for exchange rates (no key required)
- Standard configuration

## Support

See `MULTI_CURRENCY_GUIDE.md` for full documentation.

**Setup Time:** ~5 minutes  
**Status:** Ready to use immediately after migration!
