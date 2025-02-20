from collective.html2blocks import PACKAGE_NAME
from contextlib import contextmanager

import logging


logger = logging.getLogger(PACKAGE_NAME)


@contextmanager
def console_logging(logger: logging.Logger, debug: bool = False):
    """Log to console."""
    cur_level = logger.level
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(level)
    yield logger
    logger.removeHandler(handler)
    logger.setLevel(cur_level)
