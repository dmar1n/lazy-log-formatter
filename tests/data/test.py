import logging
from datetime import datetime


def log_and_return_datetime():
    now = datetime.now()
    logging.info(f"Current datetime: {now}")
    return now


class DateTimeLogger:
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def log_datetime(self):
        now = datetime.now()
        self._logger.info(f"Current datetime: {now}")
        return now
