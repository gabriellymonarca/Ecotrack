"""
Main execution module for the Investment Analyzer project.

This module serves as the entry point for the application, handling:
- Initial data updates
- Scheduler initialization
- Server startup
- Error handling and logging

The module coordinates the main components of the system:
- Data updates through the scheduler module
- Web server through the serve module
- Logging configuration for system monitoring
"""

import logging
import sys
import serve
from scheduler import update_data, start_scheduler

# Configure logging with timestamp, level and message format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """
    Main execution function that orchestrates the application startup.
    
    The function performs the following steps in sequence:
    1. Updates initial data
    2. Starts the scheduler for periodic updates
    3. Initializes the web server
    
    Each operation is wrapped in its own try-except block for specific error handling
    and logging. If any critical operation fails, the application will terminate
    with an appropriate error message.
    """
    # Initial data update
    try:
        logging.info("Updating initial data...")
        update_data()
    except Exception as e:
        logging.error(f"Failed to update initial data: {e}")
        sys.exit(1)
    
    # Scheduler initialization
    try:
        logging.info("Starting scheduler...")
        start_scheduler()
    except Exception as e:
        logging.error(f"Failed to start scheduler: {e}")
        sys.exit(1)
    
    # Server startup
    try:
        logging.info("Starting server...")
        serve.serve()
        logging.info("Server started successfully!")
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()