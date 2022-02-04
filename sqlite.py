import sqlite3
import json

from bot.bot import text_handler
from new_logging import log
from date_and_time import get_date_time
from settings import ROUTE_DB, EXEPTION_CHAT
from text_converter import num_conversion, calculation_percent, calculation_different_price, parse_items_to_send


def write_sqlite3(url):
    items = []
    sql_city = url[1][0]
    sql_chat = url[1][1]
    sql_urls_id = url[1][2]
    conn = sqlite3.connect(ROUTE_DB)
    with conn:
        cur = conn.cursor()
        cur.execute('UPDATE offers SET status=0 WHERE urls_id=?', (sql_urls_id,))  # Обнуляем у всех объявлений статус
        for i in range(0, len(url[0])):
            if url[0][i] is not None:
                sql_avito_id = url[0][i]['avito_id']
                sql_name = url[0][i]['name']
                sql_price = url[0][i]['price']
                sql_address = url[0][i]['address']
                sql_url = url[0][i]['url']
                sql_type_of = url[0][i]['type_of']
                sql_params = url[0][i]['params']

                price_history = []
                price_now = {
                    "data": str(get_date_time()),
                    "price": str(sql_price)
                }

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=?',
                            (sql_avito_id,))

                item_id = cur.fetchall()
                if item_id == [(sql_avito_id,)]:  # Ищем ID в бд, и если не находим то пишем сообщение в телегу
                    cur.execute('SELECT price FROM offers WHERE avito_id=?',
                                (sql_avito_id,))

                    item_price = cur.fetchall()
                    old_price = item_price[0][0]

                    cur.execute('SELECT price_history FROM offers WHERE avito_id=?',
                                (sql_avito_id,))

                    price_history = json.loads(cur.fetchall()[0][0])
                    price_history.append(price_now)
                    price_history_dumps = json.dumps(price_history)

                    price_history_srt = ''
                    if len(price_history) > 0:
                        for i in range(0, len(price_history)):
                            if i == 0:
                                price_history_srt = price_history_srt + \
                                                    'Дата: ' + price_history[i]['data'] + '  ' + \
                                                    'Цена: ' + num_conversion(price_history[i]['price']) + ' руб.\n'
                            else:
                                percent_price_history = calculation_percent(price_history[i - 1]['price'],
                                                                            price_history[i]['price'])
                                price_history_srt = price_history_srt + \
                                                    'Дата: ' + price_history[i]['data'] + '  ' + \
                                                    'Цена: ' + num_conversion(price_history[i]['price']) + ' руб.  ' + \
                                                    '(' + percent_price_history + '%)\n'

                        difference_price = calculation_different_price(price_history[0]['price'], price_now['price'])
                        percent_difference_price = calculation_percent(price_history[0]['price'], price_now['price'])

                    if item_price == [(sql_price,)]:  # Сравниваем цены, и если есть отличие то обновляем их
                        cur.execute(
                            "UPDATE offers SET status=1, updated_date=?,urls_id=?, type_of=?, params=? WHERE avito_id=?",
                            (str(get_date_time()), sql_urls_id, sql_type_of, sql_params, sql_avito_id))
                        continue
                    else:
                        items.append({
                            'item_price': item_price,
                            'sql_chat': sql_chat,
                            'sql_avito_id': sql_avito_id,
                            'sql_name': sql_name,
                            'old_price': old_price,
                            'sql_price': sql_price,
                            'price_history_srt': price_history_srt,
                            'difference_price': difference_price,
                            'percent_difference_price': percent_difference_price,
                            'sql_address': sql_address,
                            'sql_url': sql_url,
                            'sql_params': sql_params,
                            'sql_type_of': sql_type_of,
                            'type_update': 'update'
                        })

                        cur.execute(
                            "UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1, urls_id=?, type_of=?, params=? WHERE avito_id=?",
                            (sql_price, old_price, str(get_date_time()), str(price_history_dumps), sql_urls_id,
                             sql_type_of,
                             sql_params, sql_avito_id))
                        log.info('Price update | ' + str(sql_avito_id))

                else:
                    items.append({
                        'item_price': None,
                        'sql_chat': sql_chat,
                        'sql_avito_id': sql_avito_id,
                        'sql_name': sql_name,
                        'old_price': None,
                        'sql_price': sql_price,
                        'price_history_srt': None,
                        'difference_price': None,
                        'percent_difference_price': None,
                        'sql_address': sql_address,
                        'sql_url': sql_url,
                        'sql_params': sql_params,
                        'sql_type_of': sql_type_of,
                        'type_update': 'new'
                    })
                    log.info('No ID -> New Offer | ' + str(sql_avito_id))

                    price_history.append(price_now)
                    price_history_dumps = json.dumps(price_history)
                    cur.execute(
                        "INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url','created_date','updated_date','status','city','urls_id','type_of','params') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url,
                         str(get_date_time()), str(get_date_time()), 1, sql_city, sql_urls_id, sql_type_of, sql_params))
            else:
                error_message = 'Error: write Sql_item, item is None ' + str(sql_urls_id)
                text_handler(EXEPTION_CHAT, error_message)
                log.error(error_message)
        parse_items_to_send(items)
    conn.commit()
    conn.close()


def get_urls():
    conn = sqlite3.connect(ROUTE_DB)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id,name,city,chatid FROM urls')
        urls = cur.fetchall()
        return urls
