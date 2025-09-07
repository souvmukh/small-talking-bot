# utils/logger.py

import logging
import sys

def setup_logger():
    """
    Configures and returns a root logger for the application.

    This function sets up a logger that outputs to the console (stdout)
    with a specific format. By centralizing the logger setup, we ensure
    consistent logging throughout the application.

    Returns:
        logging.Logger: The configured root logger instance.
    """
    # Get the root logger
    logger = logging.getLogger("VoiceAssistant")
    
    # Avoid adding multiple handlers if this function is called more than once
    if not logger.handlers:
        logger.setLevel(logging.INFO)  # Set the minimum level of messages to log

        # Create a handler to print log messages to the console (standard output)
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Define the format for our log messages for clarity and consistency
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        # Add the configured handler to the logger
        logger.addHandler(console_handler)

    return logger

# Create a single logger instance to be imported by other modules
log = setup_logger()