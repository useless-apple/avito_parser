from datetime import datetime
from pytz import timezone

format = "%Y-%m-%d %H:%M:%S"

format_for_log = "%Y-%m-%d"


def get_date_time():
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(format)
    return date_and_time


def get_date_time_log():
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(format_for_log)
    return date_and_time
