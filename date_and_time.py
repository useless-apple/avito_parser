import time
from datetime import datetime
from pytz import timezone
from helpers import get_random_time


def get_date_time(time_format="%Y-%m-%d %H:%M:%S"):
    """
    Получаем текущее время
    :param time_format:
    :return:
    """
    date_and_time = datetime.now(timezone('Asia/Yekaterinburg')).strftime(time_format)
    return date_and_time


def time_sleep(n=None):
    """
    Таймер сна
    :param n:
    :return:
    """
    if n:
        time.sleep(n)
    else:
        time.sleep(get_random_time())
