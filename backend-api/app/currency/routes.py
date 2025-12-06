# app/currency/routes.py

from flask import jsonify, request, g
from app.currency import currency_bp
from app.services.currency_service import CurrencyService
from app.models import User, db
from app.utils import jwt_required
from sqlalchemy import inspect
import logging

logger = logging.getLogger(__name__)

# Import SchedulerService only if available
try:
    from app.services.scheduler_service import SchedulerService
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    logger.warning("SchedulerService not available - manual exchange rate updates disabled")


def check_currency_tables_exist():
    """Check if currency tables exist in the database."""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        return 'currencies' in tables and 'exchange_rates' in tables
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False


def currency_feature_required(f):
    """Decorator to check if currency tables exist before executing endpoint."""
    def decorated_function(*args, **kwargs):
        if not check_currency_tables_exist():
            return jsonify({
                'success': False,
                'error': 'Currency feature not available',
                'message': 'Currency tables not found. Please run the migration script: python migrate_add_currency_system.py'
            }), 503
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@currency_bp.route('/currencies', methods=['GET'])
@currency_feature_required
def get_currencies():
    """
    Get all available currencies.
    Query params:
        - active_only: boolean (default: true)
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        currencies = CurrencyService.get_all_currencies(active_only=active_only)
        
        return jsonify({
            'success': True,
            'currencies': [c.to_dict() for c in currencies],
            'count': len(currencies)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching currencies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/currencies/<code>', methods=['GET'])
@currency_feature_required
def get_currency(code):
    """Get a specific currency by code."""
    try:
        currency = CurrencyService.get_currency_by_code(code)
        
        if not currency:
            return jsonify({
                'success': False,
                'error': f'Currency {code} not found'
            }), 404
        
        # Get latest exchange rate
        latest_rate = CurrencyService.get_latest_rate(code)
        
        response = {
            'success': True,
            'currency': currency.to_dict()
        }
        
        if latest_rate:
            response['latest_rate'] = latest_rate.to_dict()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching currency {code}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/exchange-rates', methods=['GET'])
@currency_feature_required
def get_exchange_rates():
    """Get the latest exchange rates for all currencies."""
    try:
        rates = CurrencyService.get_latest_rates_for_all_currencies()
        
        return jsonify({
            'success': True,
            'rates': rates,
            'count': len(rates),
            'base_currency': 'USD'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/exchange-rates/<code>', methods=['GET'])
@currency_feature_required
def get_exchange_rate(code):
    """Get the latest exchange rate for a specific currency."""
    try:
        currency = CurrencyService.get_currency_by_code(code)
        if not currency:
            return jsonify({
                'success': False,
                'error': f'Currency {code} not found'
            }), 404
        
        latest_rate = CurrencyService.get_latest_rate(code)
        
        if not latest_rate:
            return jsonify({
                'success': False,
                'error': f'No exchange rate found for {code}'
            }), 404
        
        return jsonify({
            'success': True,
            'currency': currency.to_dict(),
            'rate': latest_rate.to_dict(),
            'base_currency': 'USD'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching exchange rate for {code}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/convert', methods=['POST'])
@currency_feature_required
def convert_currency():
    """
    Convert an amount from one currency to another.
    
    Request body:
    {
        "amount": 100.00,
        "from_currency": "USD",
        "to_currency": "PHP"
    }
    """
    try:
        data = request.get_json()
        
        amount = data.get('amount')
        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')
        
        # Validation
        if not all([amount, from_currency, to_currency]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: amount, from_currency, to_currency'
            }), 400
        
        try:
            amount = float(amount)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid amount value'
            }), 400
        
        # Perform conversion
        converted_amount, rate_used, timestamp = CurrencyService.convert_amount(
            amount, from_currency.upper(), to_currency.upper()
        )
        
        return jsonify({
            'success': True,
            'original_amount': amount,
            'original_currency': from_currency.upper(),
            'converted_amount': converted_amount,
            'target_currency': to_currency.upper(),
            'rate_used': rate_used,
            'rate_timestamp': timestamp.isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/exchange-rates/update', methods=['POST'])
@jwt_required()
@currency_feature_required
def trigger_exchange_rate_update():
    """
    Manually trigger an exchange rate update.
    Requires authentication and System Admin role.
    """
    try:
        # Check if user has System Admin role
        if g.current_user.role != 'System Admin':
            return jsonify({
                'success': False,
                'error': 'Unauthorized. System Admin role required.'
            }), 403
        
        # Check if scheduler is available
        if not SCHEDULER_AVAILABLE:
            # Fall back to direct update without scheduler
            logger.info("Scheduler not available, performing direct update")
            success = CurrencyService.update_exchange_rates()
            return jsonify({
                'success': success,
                'message': 'Exchange rate update completed' if success else 'Exchange rate update failed',
                'updated': success
            }), 200 if success else 500
        
        # Check if update is needed
        should_update = CurrencyService.should_update_rates()
        
        if not should_update:
            return jsonify({
                'success': True,
                'message': 'Exchange rates are up to date (updated within last 12 hours)',
                'updated': False
            }), 200
        
        # Trigger immediate update via scheduler
        success = SchedulerService.trigger_immediate_update()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Exchange rate update triggered successfully',
                'updated': True
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to trigger exchange rate update'
            }), 500
        
    except Exception as e:
        logger.error(f"Error triggering exchange rate update: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/user/preferred-currency', methods=['GET'])
@jwt_required()
@currency_feature_required
def get_user_preferred_currency():
    """Get the current user's preferred currency."""
    try:
        preferred_currency = g.current_user.preferred_currency or 'USD'
        currency = CurrencyService.get_currency_by_code(preferred_currency)
        
        return jsonify({
            'success': True,
            'preferred_currency': preferred_currency,
            'currency_details': currency.to_dict() if currency else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user preferred currency: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@currency_bp.route('/user/preferred-currency', methods=['PUT'])
@jwt_required()
@currency_feature_required
def update_user_preferred_currency():
    """
    Update the current user's preferred currency.
    
    Request body:
    {
        "currency_code": "PHP"
    }
    """
    try:
        data = request.get_json()
        currency_code = data.get('currency_code')
        
        if not currency_code:
            return jsonify({
                'success': False,
                'error': 'Missing required field: currency_code'
            }), 400
        
        # Validate currency exists
        currency = CurrencyService.get_currency_by_code(currency_code)
        if not currency:
            return jsonify({
                'success': False,
                'error': f'Invalid currency code: {currency_code}'
            }), 400
        
        if not currency.is_active:
            return jsonify({
                'success': False,
                'error': f'Currency {currency_code} is not active'
            }), 400
        
        # Update user's preferred currency
        g.current_user.preferred_currency = currency_code.upper()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferred currency updated successfully',
            'preferred_currency': currency_code.upper(),
            'currency_details': currency.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user preferred currency: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
