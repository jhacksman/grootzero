"""
Logging configuration for the GROOTZERO project.

This module provides utilities for setting up and using logging
throughout the GROOTZERO system.
"""

import logging
import os
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging for the GROOTZERO system.
    
    Args:
        log_level: The logging level to use. One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
        log_file: Path to the log file. If None, logs are only output to the console.
        
    Returns:
        The configured logger instance.
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logger = logging.getLogger("grootzero")
    logger.setLevel(numeric_level)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()


def get_logger(name: str = "grootzero") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name of the logger. Defaults to "grootzero".
        
    Returns:
        The logger instance.
    """
    return logging.getLogger(name)
