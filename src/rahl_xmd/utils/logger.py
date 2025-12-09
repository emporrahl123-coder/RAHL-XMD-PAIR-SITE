"""
Logging utilities for RAHL XMD.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import colorama

colorama.init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors."""
    
    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT,
    }
    
    RESET = colorama.Style.RESET_ALL
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)


def setup_logger(name: str, 
                level: str = "INFO",
                log_to_file: bool = True,
                log_dir: str = "logs") -> logging.Logger:
    """
    Setup and configure logger.
    
    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_path / f"rahl_xmd_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance.
    
    Args:
        name: Logger name (defaults to 'rahl_xmd')
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "rahl_xmd"
    
    return logging.getLogger(name)
