"""Logging configuration for GroupFolio bot"""
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging():
    """Set up logging with both file and console handlers"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('groupfolio')
    logger.setLevel(logging.DEBUG)

    logger.handlers = []

    file_handler = RotatingFileHandler(
        'logs/groupfolio.log',
        maxBytes=5_000_000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
