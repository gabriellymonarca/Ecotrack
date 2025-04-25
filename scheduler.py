"""
Scheduler module for the Investment Analyzer project.

This module handles:
- Periodic data updates through a background scheduler
- Data fetching, population and aggregation pipeline
- Error handling and logging for the update process

The module uses APScheduler for scheduling tasks and coordinates
the data update pipeline across multiple components.
"""

import fetch
import logging
import populate
import aggregate
import serve

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def update_data():
    """
    Executes the complete data update pipeline.
    
    The pipeline consists of three main steps:
    1. Fetching data from external sources
    2. Populating the data into the system
    3. Aggregating the data for analysis
    
    Each step is wrapped in error handling to ensure proper logging
    and system stability.
    """
    logging.info("Starting data update process...")
    
    # Step 1: Fetch data
    try:
        logging.info("Starting data fetch...")
        fetch_result = fetch.fetch()
        logging.info("Data fetched successfully!")
    except Exception as e:
        logging.error(f"Error during data fetch: {e}")
        raise
    
    # Step 2: Populate data
    try:
        logging.info("Starting data population...")
        populate_result = populate.populate(fetch_result)
        logging.info("Data populated successfully!")
    except Exception as e:
        logging.error(f"Error during data population: {e}")
        raise
    
    # Step 3: Aggregate data
    try:
        logging.info("Starting data aggregation...")
        aggregate_result = aggregate.aggregate(populate_result)
        logging.info("Data aggregated successfully!")
    except Exception as e:
        logging.error(f"Error during data aggregation: {e}")
        raise

    # Update the application data
    try:
        serve.app_data = aggregate_result
        logging.info("Update process completed successfully!")
    except Exception as e:
        logging.error(f"Error updating application data: {e}")
        raise
        
def start_scheduler():
    """
    Initializes and starts the background scheduler.
    
    The scheduler is configured to run the update_data function
    at 2:00 AM on the first day of each month.
    """
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_data, CronTrigger.from_crontab('0 2 1 * *'))
        scheduler.start()
        logging.info("Scheduler started successfully.")
    except Exception as e:
        logging.error(f"Failed to start scheduler: {e}")
        raise