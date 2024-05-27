"""Logging functions."""
import sys
import logging

# the global logging.Logger object, initialized by init_logging()
logger: logging.Logger


def init_logging(stream=sys.stderr):
    """Initialize the global logger. All log messages will be
    sent to the given stream, default is sys.stderr.
    """
    global logger
    logger = logging.getLogger('Mdownloader')
    handler = logging.StreamHandler(stream=stream)
    log_format = f"%(levelname)s Mdownloader: %(message)s"
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_error(msg):
    """Log error message."""
    logger.error(msg)


init_logging()