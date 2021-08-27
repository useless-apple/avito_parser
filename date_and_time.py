from datetime import datetime
from pytz import timezone

format = "%Y-%m-%d %H:%M:%S"


def get_date_time():
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(format)
    return date_and_time
