# utils/logger.py
import logging
import sys
import os


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels for console output.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }

    RESET = "\033[0m"  # Reset color

    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)

        # Add color for console output
        if record.levelname in self.COLORS:
            log_message = f"{self.COLORS[record.levelname]}{log_message}{self.RESET}"

        return log_message


def setup_logger():
    """
    Configures and returns a root logger for the application.

    This function sets up a logger that outputs to both the console (stdout)
    with colored formatting and to a log file with standard formatting.
    By centralizing the logger setup, we ensure consistent logging
    throughout the application.

    Returns:
        logging.Logger: The configured root logger instance.
    """
    # Get the root logger
    logger = logging.getLogger("VoiceAssistant")

    # Avoid adding multiple handlers if this function is called more than once
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Define the format for our log messages for clarity and consistency
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Console Handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Only INFO and above to console
        colored_formatter = ColoredFormatter(log_format, datefmt=date_format)
        console_handler.setFormatter(colored_formatter)

        # File Handler for app.log (without colors)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "app.log"), mode="a", encoding="utf-8"  # Append mode
        )
        file_handler.setLevel(logging.DEBUG)  # All levels to file
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)

        # Add both handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Log the initialization
        logger.info("Logger initialized with colored console output and file logging")

    return logger


log = setup_logger()
