import requests
from bs4 import BeautifulSoup
import time
import random
import cfscrape
import json
import logging
from date_and_time import get_date_time

from bot.bot import text_handler
from settings import exception_chat
from sqlite import write_sqlite3, get_urls
from text_converter import clean

date_and_time = get_date_time()

logging.basicConfig(filename="logging.log", level=logging.INFO, format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',)
log = logging.getLogger("ex")

def get_session():
    session = requests.Session()
    session.headers = {
        'Host': 'www.avito.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)   Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html',
        'Accept-Language': 'ru,en-US;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'}
    return cfscrape.create_scraper(sess=session)


def get_item_data(rows, type_of):
    result = []
    for row in rows:
        try:
            avito_id = int(row.get('data-item-id'))
        except:
            avito_id = 'Не найден'

        try:
            name = clean(row.find('h3', {"itemprop": "name"}).text)
        except:
            name = 'Не найден'

        try:
            price = int(clean(row.find('meta', {"itemprop": "price"}).get("content")))
        except:
            price = 'Не найден'

        try:
            url = 'https://avito.ru' + row.find('a', {"itemprop": "url"}).get("href")
        except:
            url = 'Не найден'

        if type_of == 'Недвижимость':
            try:
                address = clean(row.find('div', {"data-marker": "item-address"}).div.span.span.text)
            except:
                address = 'Не найден'
        else:
            address = 'None'

        if type_of == 'Транспорт':
            try:
                params = clean(row.find('div', {"data-marker": "item-specific-params"}).text)
            except:
                params = 'Не найден'
        else:
            params = 'None'
        item = {'avito_id': avito_id, 'name': name, 'price': price, 'address': address, 'url': url, 'type_of': type_of,
                'params': params}
        result.append(item)
    return result


def get_page_data(page_url):
    session = get_session()
    r = session.get(page_url)
    if r.status_code == 200:
        time.sleep(1)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            type_of = soup.find('div', {"data-marker": "breadcrumbs"}).find_all('span', {"itemprop": "itemListElement"})[
                1].find('a').text
        except:
            type_of = 'None Type'
        table = soup.find('div', {"data-marker": "catalog-serp"})
        if table:
            if table.find('div', {"data-marker": "witcher/block"}):
                table.find('div', {"data-marker": "witcher/block"}).decompose()
        if not table:
            error_message = 'Error not table' + str(soup) + str(table)
            logging.error(error_message)
            text_handler(exception_chat, error_message)
            print(soup)
            print(table)
            result = []
        else:
            rows = table.find_all('div', {"data-marker": "item"})
            result = get_item_data(rows, type_of)
    else:
        error_message = 'Error not table' + str(r.status_code)
        text_handler(exception_chat, error_message)
        logging.error('Error:' + str(r.status_code))
        print('Error:' + str(r.status_code))
        result = []
    return result


def write_json_txt(result, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def main(main_url):
    log.info('Starting parsing ' + str(date_and_time))
    print(str(date_and_time))
    global_result = []
    for task in main_url:
        url_task = task[1]
        task = [task[2], task[3], task[0]]
        log.info('Url parsing ' + str(url_task))
        print(url_task)
        session = get_session()
        r = session.get(url_task + '&p=1')
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                pagination = soup.find('div', {"data-marker": "pagination-button"})
                pagination.find('span', {"data-marker": "pagination-button/prev"}).decompose()
                pagination.find('span', {"data-marker": "pagination-button/next"}).decompose()
                count_page = pagination.find_all('span')[-1].text
            except:
                count_page = 1
                error_message = 'Error pagination'
                text_handler(exception_chat, error_message)
                logging.error('Error pagination')
            result = []
            for i in range(1, int(count_page) + 1):
                value = random.random()
                scaled_value = 4 + (value * (11 - 5))
                log.info('Parsing page# ' + str(i) + ' of ' + count_page)
                print('Parsing page# ' + str(i) + ' of ' + count_page)
                page_url = url_task + '&p=' + str(i)
                result += get_page_data(page_url)
                time.sleep(scaled_value)
            value = random.random()
            scaled_value = 4 + (value * (11 - 5))
            time.sleep(scaled_value)
            item = [result, task]
            write_sqlite3(item)
            global_result.append(item)
        else:
            error_message = 'Error: ' + str(r.status_code)
            text_handler(exception_chat, error_message)
            logging.error(error_message)
            print('Error: ' + str(r.status_code))

    write_json_txt(global_result, 'data.json')
    log.info('Parsing Success')
    print('Parsing Success')
    #write_sqlite3(global_result)


if __name__ == '__main__':
    try:
        main_url = []
        main_url += get_urls()
        main(main_url)
        # with open('data_item.json', encoding='utf-8', newline='') as json_file:
        #     data = json.load(json_file)
        #     write_sqlite3(data)
    except Exception as e:
        log.exception(str(e))