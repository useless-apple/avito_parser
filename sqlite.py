import sqlite3
import json

from bot.bot import text_handler
from new_logging import log
from date_and_time import get_date_time, time_sleep
from settings import ROUTE_DB, EXEPTION_CHAT
from text_converter import num_conversion, calculation_percent, calculation_different_price, send_mes_to_bot


def write_sqlite3(url):
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
                price_now = [str(get_date_time()), str(sql_price)]

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
                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)

                    price_history_srt = ''
                    if len(price_history) > 0:
                        for i in range(0, len(price_history), 2):
                            if i != 0 and i != 1:
                                percent_price_history = calculation_percent(price_history[i - 1], price_history[i + 1])
                                price_history_srt = price_history_srt + \
                                                    'Дата: ' + price_history[i][0:10] + '  ' + \
                                                    'Цена: ' + num_conversion(price_history[i + 1]) + ' руб.  ' + \
                                                    '(' + percent_price_history + '%)\n'

                            else:
                                price_history_srt = price_history_srt + \
                                                    'Дата: ' + price_history[i][0:10] + '  ' + \
                                                    'Цена: ' + num_conversion(price_history[i + 1]) + ' руб.\n'

                        difference_price = calculation_different_price(price_history[1], price_now[1])
                        percent_difference_price = calculation_percent(price_history[1], price_now[1])

                    if item_price == [(sql_price,)]:  # Сравниваем цены, и если есть отличие то обновляем их
                        cur.execute(
                            "UPDATE offers SET status=1, updated_date=?,urls_id=?, type_of=?, params=? WHERE avito_id=?",
                            (str(get_date_time()), sql_urls_id, sql_type_of, sql_params, sql_avito_id))
                        continue
                    else:
                        send_mes_to_bot(item_price, sql_chat, sql_avito_id, sql_name,
                                        old_price, sql_price, price_history_srt,
                                        difference_price, percent_difference_price,
                                        sql_address, sql_url, sql_params,
                                        sql_type_of, 'update')

                        cur.execute(
                            "UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1, urls_id=?, type_of=?, params=? WHERE avito_id=?",
                            (sql_price, old_price, str(get_date_time()), str(price_history_dumps), sql_urls_id,
                             sql_type_of,
                             sql_params, sql_avito_id))
                        log.info('Price update | ' + str(sql_avito_id))
                        time_sleep(5)

                else:
                    send_mes_to_bot(None, sql_chat, sql_avito_id, sql_name, None, sql_price, None,
                                    None, None, sql_address, sql_url, sql_params,
                                    sql_type_of, 'new')
                    log.info('No ID -> New Offer | ' + str(sql_avito_id))

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    cur.execute(
                        "INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url','created_date','updated_date','status','city','urls_id','type_of','params') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url,
                         str(get_date_time()), str(get_date_time()), 1, sql_city, sql_urls_id, sql_type_of, sql_params))
                    time_sleep(5)
            else:
                error_message = 'Error: write Sql_item, item is None ' + str(sql_urls_id)
                text_handler(EXEPTION_CHAT, error_message)
                log.error(error_message)
    conn.commit()
    conn.close()


def get_urls():
    conn = sqlite3.connect(ROUTE_DB)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id,name,city,chatid FROM urls')
        urls = cur.fetchall()
        return urls
