"""
Logging system for the Dark War Survival Bot
"""

import logging
import os
import sys
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging(log_level: str = "INFO", save_to_file: bool = True):
    """Set up logging configuration"""

    # Create logs directory
    if save_to_file:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/bot_{timestamp}.log"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if enabled)
    if save_to_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always save all levels to file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    return logger

def log_bot_stats(stats: dict):
    """Log bot statistics in a formatted way"""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("BOT STATISTICS")
    logger.info("=" * 60)

    for category, data in stats.items():
        logger.info(f"{category.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {data}")
        logger.info("")

    logger.info("=" * 60)

def log_error_with_screenshot(error_msg: str, screenshot_path: str = None):
    """Log error with optional screenshot"""
    logger = logging.getLogger(__name__)
    logger.error(error_msg)

    if screenshot_path:
        logger.error(f"Screenshot saved: {screenshot_path}")

def log_task_start(task_name: str, cycle: int = None):
    """Log the start of a task"""
    logger = logging.getLogger(__name__)
    cycle_info = f" (Cycle {cycle})" if cycle else ""
    logger.info(f"Starting task: {Fore.CYAN}{task_name}{Style.RESET_ALL}{cycle_info}")

def log_task_complete(task_name: str, duration: float):
    """Log task completion"""
    logger = logging.getLogger(__name__)
    logger.info(f"Task completed: {Fore.GREEN}{task_name}{Style.RESET_ALL} in {duration:.1f}s")

def log_task_failed(task_name: str, error: str):
    """Log task failure"""
    logger = logging.getLogger(__name__)
    logger.error(f"Task failed: {Fore.RED}{task_name}{Style.RESET_ALL} - {error}")