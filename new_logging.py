import logging
from date_and_time import get_date_time, get_date_time_log
from settings import DIR_LOCATION
date_and_time = get_date_time()

logging.basicConfig(
    filename="{0}logs/log-{1}.log".format(DIR_LOCATION, get_date_time_log()),
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
)
log = logging.getLogger("ex")