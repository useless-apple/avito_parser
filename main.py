import re
import requests
from bs4 import BeautifulSoup
import time
import random
import sqlite3
from datetime import datetime
import json
from bot.bot import text_handler
from bot.settings import except_chat
from get_proxy import get_html
from settings import route_db

emoji_top = u'\U0001F4C8'
emoji_top_green = u'\U00002705'

emoji_down = u'\U0001F4C9'
emoji_down_red = u'\U0000274C'


def write_sqlite3(result):
    conn = sqlite3.connect(route_db)
    for url in result:
        with conn:
            cur = conn.cursor()
            cur.execute('UPDATE offers SET status=0 WHERE city =?', (url[1][0],))
            for i in range(0, len(url[0])):
                sql_avito_id = url[0][i]['avito_id']
                sql_name = url[0][i]['name']
                sql_price = url[0][i]['price']
                sql_address = url[0][i]['address']
                sql_url = url[0][i]['url']
                price_history = []
                price_now = [str(datetime.utcnow()), str(sql_price)]

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=? AND city =?', (sql_avito_id, url[1][0]))
                item_id = cur.fetchall()
                if item_id == [(sql_avito_id,)]:
                    cur.execute('SELECT price FROM offers WHERE avito_id=? AND city =?', (sql_avito_id, url[1][0]))
                    item_price = cur.fetchall()

                    cur.execute('SELECT price_history FROM offers WHERE avito_id=? AND city =?',
                                (sql_avito_id, url[1][0]))
                    price_history = json.loads(cur.fetchall()[0][0])
                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    price_history_srt = ''
                    if len(price_history) > 0:
                        for i in range(0, len(price_history), 2):
                            price_history_srt = price_history_srt + 'Дата: ' + price_history[i][0:10] + '  Цена:' + \
                                                price_history[i + 1] + ' руб.\n'
                    if (item_price == [(sql_price,)]):
                        cur.execute("UPDATE offers SET status=1, updated_date=? WHERE avito_id=? AND city =?",
                                    (str(datetime.utcnow()), sql_avito_id, url[1][0]))
                        continue
                    else:
                        if (item_price >= [(sql_price,)]):
                            text_handler(url[1][1], 'Обновилась цена id ' + str(
                                sql_avito_id) + '  ' + emoji_down + emoji_down + emoji_top_green + '\n Старая цена = ' + str(
                                item_price[0][0]) + ' руб. / Новая цена = ' + str(
                                sql_price) + ' руб.\n\nИзменения цен \n' + str(price_history_srt) + '\n\nАдрес: ' + str(
                                sql_address) + '\n\nСсылка ' + str(sql_url))
                        else:
                            text_handler(url[1][1], 'Обновилась цена id ' + str(
                                sql_avito_id) + '  ' + emoji_top + emoji_top + emoji_down_red + '\n Старая цена = ' + str(
                                item_price[0][0]) + ' руб. / Новая цена = ' + str(
                                sql_price) + ' руб.\n\nИзменения цен \n' + str(price_history_srt) + '\n\nАдрес: ' + str(
                                sql_address) + '\n\nСсылка ' + str(sql_url))

                        cur.execute(
                            "UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1 WHERE avito_id=? AND city =?",
                            (
                                sql_price, item_price[0][0], str(datetime.utcnow()), str(price_history_dumps),
                                sql_avito_id,
                                url[1][0]))
                        print('Price update ' + str(sql_avito_id))
                        time.sleep(5)

                else:
                    text_handler(url[1][1], 'Новое объявление ' + str(sql_avito_id) + '\n\nЦена: ' + str(
                        sql_price) + ' руб.' + '\n\nАдрес: ' + str(sql_address) + '\n\nСсылка ' + str(sql_url))
                    print('New Offer ' + str(sql_avito_id))

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    cur.execute(
                        "INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url',"
                        "'created_date','updated_date','status','city') VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url,
                         str(datetime.utcnow()), str(datetime.utcnow()), 1, url[1][0]))
                    time.sleep(5)
    conn.commit()
    conn.close()


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
                print(soup.find_all('span', attrs={"class": re.compile(r"pagination-item")}))
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
