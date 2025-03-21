import logging
import sys

def setup_logger(log_file="jarvis.log", level=logging.DEBUG):
    """
    Set up the logger to log messages to both the console and a file.
    """
    logger = logging.getLogger("Jarvis")
    logger.setLevel(level)

    # Ensure UTF-8 encoding
    sys.stdout.reconfigure(encoding="utf-8")

    # Formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")  # Force UTF-8 encoding
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

def get_logger(name):
    """
    Retrieve a logger with the specified name.
    """
    return logging.getLogger(name)
