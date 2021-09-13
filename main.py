from date_and_time import get_date_time
from helpers import write_json_txt
from new_logging import log
from parser_avito import get_global_result
from sqlite import get_urls


if __name__ == '__main__':
    try:
        log.info('-----------------------------------------------------------------------------------------------')
        log.info('Starting parsing ' + str(get_date_time()))
        tasks = []
        tasks += get_urls()
        global_result = get_global_result(tasks)
        write_json_txt(global_result, 'data.json')
        log.info('Parsing Success ' + str(get_date_time()))
        log.info('-----------------------------------------------------------------------------------------------')
        # with open('data_item.json', encoding='utf-8', newline='') as json_file:
        #     data = json.load(json_file)
        #     write_sqlite3(data)
    except Exception as e:
        log.exception(str(e))
