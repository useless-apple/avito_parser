import re

from date_and_time import get_date_time
from helpers import write_json_txt, read_json_txt
from new_logging import log
from parser_avito import get_global_result
from sqlite import get_urls, write_sqlite3

if __name__ == '__main__':
    try:
        log.info('-----------------------------------------------------------------------------------------------')
        log.info('Starting parsing ' + str(get_date_time()))
        tasks = []
        tasks += get_urls()
        write_json_txt(tasks, 'data_task.json')
        global_result = get_global_result(tasks)
        write_json_txt(global_result, 'data.json')
        log.info('Parsing Success ' + str(get_date_time()))
        log.info('-----------------------------------------------------------------------------------------------')

    except Exception as e:
        log.exception(str(e))
