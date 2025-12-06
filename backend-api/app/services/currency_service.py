# app/services/currency_service.py

from app.models import Currency, ExchangeRate, db
from datetime import datetime, timedelta
from sqlalchemy import desc
import requests
import logging

logger = logging.getLogger(__name__)

# Currency catalog with common currencies including Philippine Peso
CURRENCY_CATALOG = [
    {'code': 'USD', 'name': 'United States Dollar', 'symbol': '$'},
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
    {'code': 'GBP', 'name': 'British Pound Sterling', 'symbol': '£'},
    {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
    {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥'},
    {'code': 'PHP', 'name': 'Philippine Peso', 'symbol': '₱'},
    {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'CA$'},
    {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$'},
    {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF'},
    {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹'},
    {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩'},
    {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$'},
    {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$'},
    {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': 'MX$'},
    {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$'},
    {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R'},
    {'code': 'NZD', 'name': 'New Zealand Dollar', 'symbol': 'NZ$'},
    {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr'},
    {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr'},
    {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr'},
    {'code': 'THB', 'name': 'Thai Baht', 'symbol': '฿'},
    {'code': 'MYR', 'name': 'Malaysian Ringgit', 'symbol': 'RM'},
    {'code': 'IDR', 'name': 'Indonesian Rupiah', 'symbol': 'Rp'},
    {'code': 'VND', 'name': 'Vietnamese Dong', 'symbol': '₫'},
]


class CurrencyService:
    """Service for managing currencies and exchange rates."""
    
    @staticmethod
    def initialize_currencies():
        """
        Initialize the currency catalog in the database.
        Only adds currencies that don't already exist.
        """
        added_count = 0
        for currency_data in CURRENCY_CATALOG:
            existing = Currency.query.filter_by(code=currency_data['code']).first()
            if not existing:
                currency = Currency(
                    code=currency_data['code'],
                    name=currency_data['name'],
                    symbol=currency_data['symbol'],
                    is_active=True
                )
                db.session.add(currency)
                added_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Currency initialization complete. Added {added_count} new currencies.")
            return added_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing currencies: {e}")
            raise
    
    @staticmethod
    def get_all_currencies(active_only=True):
        """Get all currencies from the database."""
        query = Currency.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Currency.code).all()
    
    @staticmethod
    def get_currency_by_code(code):
        """Get a specific currency by its code."""
        return Currency.query.filter_by(code=code.upper()).first()
    
    @staticmethod
    def fetch_exchange_rates_from_api():
        """
        Fetch current exchange rates from an external API.
        Uses exchangerate-api.com (free tier, 1500 requests/month).
        Returns dict of currency codes to rates (relative to USD).
        """
        try:
            # Using exchangerate-api.com with USD as base
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            logger.info(f"Successfully fetched exchange rates for {len(rates)} currencies")
            return rates
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange rates from API: {e}")
            return None
    
    @staticmethod
    def update_exchange_rates():
        """
        Update exchange rates for all active currencies.
        Should be called every 12 hours via a scheduler.
        """
        rates = CurrencyService.fetch_exchange_rates_from_api()
        
        if not rates:
            logger.warning("Could not fetch exchange rates, skipping update")
            return False
        
        updated_count = 0
        timestamp = datetime.utcnow()
        
        # Get all active currencies
        currencies = Currency.query.filter_by(is_active=True).all()
        
        for currency in currencies:
            code = currency.code
            
            # USD to USD is always 1.0
            if code == 'USD':
                rate_from_usd = 1.0
                rate_to_usd = 1.0
            elif code in rates:
                # rate_from_usd: How many units of foreign currency for 1 USD
                # rate_to_usd: How many USD for 1 unit of foreign currency
                rate_from_usd = rates[code]
                rate_to_usd = 1.0 / rate_from_usd if rate_from_usd != 0 else 0
            else:
                logger.warning(f"No rate found for {code}, skipping")
                continue
            
            # Check if we already have a recent rate (within last 11 hours)
            recent_rate = ExchangeRate.query.filter_by(currency_code=code)\
                .filter(ExchangeRate.timestamp > timestamp - timedelta(hours=11))\
                .order_by(desc(ExchangeRate.timestamp))\
                .first()
            
            if recent_rate:
                logger.info(f"Recent rate exists for {code}, skipping")
                continue
            
            # Create new exchange rate entry
            exchange_rate = ExchangeRate(
                currency_code=code,
                rate_to_usd=rate_to_usd,
                rate_from_usd=rate_from_usd,
                timestamp=timestamp,
                source='exchangerate-api'
            )
            db.session.add(exchange_rate)
            updated_count += 1
        
        try:
            db.session.commit()
            logger.info(f"Exchange rate update complete. Updated {updated_count} rates.")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating exchange rates: {e}")
            return False
    
    @staticmethod
    def get_latest_rate(currency_code):
        """Get the most recent exchange rate for a currency."""
        return ExchangeRate.query.filter_by(currency_code=currency_code)\
            .order_by(desc(ExchangeRate.timestamp))\
            .first()
    
    @staticmethod
    def get_latest_rates_for_all_currencies():
        """Get the most recent exchange rate for each active currency."""
        currencies = Currency.query.filter_by(is_active=True).all()
        rates = {}
        
        for currency in currencies:
            latest_rate = CurrencyService.get_latest_rate(currency.code)
            if latest_rate:
                rates[currency.code] = {
                    'currency': currency.to_dict(),
                    'rate': latest_rate.to_dict()
                }
        
        return rates
    
    @staticmethod
    def convert_amount(amount, from_currency, to_currency):
        """
        Convert an amount from one currency to another.
        Always converts through USD as the base currency.
        
        Args:
            amount: The amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            tuple: (converted_amount, rate_used, timestamp)
        """
        # If same currency, no conversion needed
        if from_currency == to_currency:
            return (amount, 1.0, datetime.utcnow())
        
        # Get latest rates for both currencies
        from_rate = CurrencyService.get_latest_rate(from_currency)
        to_rate = CurrencyService.get_latest_rate(to_currency)
        
        if not from_rate or not to_rate:
            raise ValueError(f"Exchange rate not found for {from_currency} or {to_currency}")
        
        # Convert to USD first, then to target currency
        amount_in_usd = float(amount) * float(from_rate.rate_to_usd)
        converted_amount = amount_in_usd * float(to_rate.rate_from_usd)
        
        # Calculate the effective rate
        rate_used = float(to_rate.rate_from_usd) / float(from_rate.rate_to_usd) if float(from_rate.rate_to_usd) != 0 else 0
        
        # Use the older timestamp of the two rates
        timestamp = min(from_rate.timestamp, to_rate.timestamp)
        
        return (round(converted_amount, 2), round(rate_used, 6), timestamp)
    
    @staticmethod
    def should_update_rates():
        """
        Check if exchange rates need to be updated.
        Returns True if the most recent rate is older than 12 hours.
        """
        latest_rate = ExchangeRate.query.order_by(desc(ExchangeRate.timestamp)).first()
        
        if not latest_rate:
            return True
        
        time_since_update = datetime.utcnow() - latest_rate.timestamp
        return time_since_update > timedelta(hours=12)
