import re
import time
import random
import sqlite3
import json
from datetime import datetime
from bs4 import BeautifulSoup
from bot.bot import text_handler
from settings import except_chat
from get_proxy import get_html
from settings import route_db
from write_sql import write_sqlite3


def clean(text):
    return text.replace('\t', '').replace('\n', '').strip()


def get_page_data(page_url):
    r = get_html(page_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('div', {"data-marker": "catalog-serp"})
        if table:
            if table.find('div', {"data-marker": "witcher/block"}):
                table.find('div', {"data-marker": "witcher/block"}).decompose()
        if not table:
            text_handler(except_chat, soup)
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
                    avito_id = 0
                try:
                    name = clean(row.find('h3', {"itemprop": "name"}).text)
                except:
                    name = ''
                try:
                    price = int(clean(row.find('meta', {"itemprop": "price"}).get("content")))
                except:
                    price = 0
                try:
                    url = 'https://avito.ru' + row.find('a', {"itemprop": "url"}).get("href")
                except:
                    url = ''
                try:
                    address = clean(row.find('span', {"class": "geo-address-9QndR"}).text)
                except:
                    address = ''
                item = {'avito_id': avito_id, 'name': name, 'price': price, 'address': address, 'url': url, }
                result.append(item)
    else:
        print('Error:' + str(r.status_code))
        result = []
    return result


def get_urls():
    conn = sqlite3.connect(route_db)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT name,city,chatid FROM urls')
        urls = cur.fetchall()
        return urls


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
        r = get_html(url_task + '&p=1')
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                count_page = soup.find_all('span', attrs={"class": re.compile(r"pagination-item")})[-2].text
            except:
                text_handler(except_chat, soup)
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
            text_handler(except_chat, 'Error:' + str(r.status_code))
            print('Error:' + str(r.status_code))

    write_json_txt(global_result)
    write_sqlite3(global_result)


if __name__ == '__main__':
    main_url = []
    main_url += get_urls()
    main(main_url)
