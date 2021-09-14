import logging
from date_and_time import get_date_time
from settings import DIR_LOCATION

logging.basicConfig(
    filename="{0}logs/log-{1}.log".format(DIR_LOCATION, get_date_time("%Y-%m-%d")),
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
)
log = logging.getLogger("ex")