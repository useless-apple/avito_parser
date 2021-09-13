from datetime import datetime
import time
from pytz import timezone

from helpers import get_random_time

format = "%Y-%m-%d %H:%M:%S"

format_for_log = "%Y-%m-%d"


def get_date_time():
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(format)
    return date_and_time


def get_date_time_log():
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(format_for_log)
    return date_and_time


def time_sleep(n=None):
    if n:
        time.sleep(n)
    else:
        time.sleep(get_random_time())