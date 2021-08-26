import requests
from bs4 import BeautifulSoup
import time
import random
import cfscrape
import json
from datetime import datetime

from bot.bot import text_handler
from settings import exception_chat
from sqlite import write_sqlite3, get_urls
from text_converter import clean


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


def get_page_data(page_url):
    session = get_session()
    r = session.get(page_url)
    if r.status_code == 200:
        time.sleep(1)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('div', {"data-marker": "catalog-serp"})
        if table:
            if table.find('div', {"data-marker": "witcher/block"}):
                table.find('div', {"data-marker": "witcher/block"}).decompose()
        if not table:
            error_message = 'Error not table' + str(soup) + str(table)
            text_handler(exception_chat, error_message)
            print(soup)
            print(table)
            result = []
        else:
            rows = table.find_all('div', {"data-marker": "item"})
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

                try:
                    address = clean(row.find('div', {"data-marker": "item-address"}).div.span.span.text)
                except:
                    address = 'Не найден'

                item = {'avito_id': avito_id, 'name': name, 'price': price, 'address': address, 'url': url, }
                result.append(item)
    else:
        error_message = 'Error not table' + str(r.status_code)
        text_handler(exception_chat, error_message)
        print('Error:' + str(r.status_code))
        result = []
    return result


def write_json_txt(result):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def main(main_url):
    print(str(datetime.utcnow()))
    global_result = []
    for task in main_url:
        url_task = task[0]
        task = [task[1], task[2]]

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
                print('Error pagination')
            result = []
            for i in range(1, int(count_page) + 1):
                value = random.random()
                scaled_value = 4 + (value * (11 - 5))
                print('Parsing page# ' + str(i) + ' of ' + count_page)
                page_url = url_task + '&p=' + str(i)
                result += get_page_data(page_url)
                time.sleep(scaled_value)
            value = random.random()
            scaled_value = 4 + (value * (11 - 5))
            time.sleep(scaled_value)
            item = [result, task]
            global_result.append(item)
        else:
            error_message = 'Error not table' + str(r.status_code)
            text_handler(exception_chat, error_message)
            print('Error:' + str(r.status_code))

    write_json_txt(global_result)
    write_sqlite3(global_result)


if __name__ == '__main__':
    # main_url = []
    # main_url += get_urls()
    # main(main_url)
    with open('data.json', encoding='utf-8', newline='') as json_file:
        data = json.load(json_file)
        write_sqlite3(data)
