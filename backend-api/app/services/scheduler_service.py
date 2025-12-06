# app/services/scheduler_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.currency_service import CurrencyService
from datetime import datetime
import logging
import atexit

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling periodic tasks like exchange rate updates."""
    
    _scheduler = None
    _initialized = False
    
    @classmethod
    def initialize(cls, app):
        """
        Initialize the scheduler with the Flask app context.
        Sets up automatic exchange rate updates every 12 hours.
        """
        if cls._initialized:
            logger.warning("Scheduler already initialized")
            return
        
        cls._scheduler = BackgroundScheduler(daemon=True)
        
        # Store app context for use in scheduled jobs
        cls._app = app
        
        # Add job to update exchange rates every 12 hours
        cls._scheduler.add_job(
            func=cls._update_exchange_rates_job,
            trigger=IntervalTrigger(hours=12),
            id='update_exchange_rates',
            name='Update currency exchange rates',
            replace_existing=True,
            max_instances=1
        )
        
        # Start the scheduler
        cls._scheduler.start()
        cls._initialized = True
        
        logger.info("Scheduler initialized successfully")
        
        # Ensure scheduler shuts down cleanly on app exit
        atexit.register(cls.shutdown)
        
        # Run initial update on startup (in background)
        cls._scheduler.add_job(
            func=cls._update_exchange_rates_job,
            trigger='date',
            run_date=datetime.now(),
            id='initial_exchange_rate_update',
            name='Initial exchange rate update'
        )
    
    @classmethod
    def _update_exchange_rates_job(cls):
        """Job function to update exchange rates within app context."""
        with cls._app.app_context():
            try:
                logger.info("Starting scheduled exchange rate update")
                success = CurrencyService.update_exchange_rates()
                if success:
                    logger.info("Scheduled exchange rate update completed successfully")
                else:
                    logger.warning("Scheduled exchange rate update failed")
            except Exception as e:
                logger.error(f"Error in scheduled exchange rate update: {e}")
    
    @classmethod
    def shutdown(cls):
        """Shutdown the scheduler gracefully."""
        if cls._scheduler and cls._scheduler.running:
            cls._scheduler.shutdown(wait=False)
            logger.info("Scheduler shut down successfully")
    
    @classmethod
    def get_scheduler(cls):
        """Get the scheduler instance."""
        return cls._scheduler
    
    @classmethod
    def trigger_immediate_update(cls):
        """Manually trigger an immediate exchange rate update."""
        if not cls._initialized:
            logger.error("Scheduler not initialized")
            return False
        
        try:
            cls._scheduler.add_job(
                func=cls._update_exchange_rates_job,
                trigger='date',
                run_date=datetime.now(),
                id='manual_exchange_rate_update',
                name='Manual exchange rate update',
                replace_existing=True
            )
            logger.info("Manual exchange rate update triggered")
            return True
        except Exception as e:
            logger.error(f"Error triggering manual update: {e}")
            return False
