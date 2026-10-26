"""
logger.py
---------
Central logging configuration.
Provides a consistent logger with rotating file output and console output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent

_logger_instance = None

def setup_logger(name="PythonToolbox"):
    """
    Sets up the central logger for the project if not already done.
    Implements idempotency to prevent duplicate log entries on multiple imports.

    Returns:
    --------
    logging.logger
        The configured logger object for the pipeline.
    """

    global _logger_instance
    if _logger_instance is not None:
        return _logger_instance
    
    log_dir = BASE_PATH / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    logger = logging.getLogger(name)
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, None)
    if level is None:
        print(f"warning : Unknown loglevel '{level_name}', use INFO")
        level = logging.INFO
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        file_handler =  RotatingFileHandler(
            log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
            )
        
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    logger.propagate = False

    _logger_instance = logger 
    return logger

logger = setup_logger()

if __name__ == "__main__":
    logger.info("Test-Log: Successfully set up the logger.")
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Testingfailure without traceback: {e}")
        logger.error(f"Testingfailure with Traceback:", exc_info=True)