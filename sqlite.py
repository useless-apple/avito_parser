import sqlite3
import json
import time

from date_and_time import get_date_time
from settings import route_db
from text_converter import num_conversion, calculation_percent, calculation_different_price, \
    calculation_percent_different_price, send_mes_to_bot

date_and_time = get_date_time()


def write_sqlite3(result):
    conn = sqlite3.connect(route_db)
    with conn:
        cur = conn.cursor()
        #Обнуляем у всех объявлений статус
        cur.execute('UPDATE offers SET status=0',())
        for url in result:
            for i in range(0, len(url[0])):
                sql_avito_id = url[0][i]['avito_id']
                sql_name = url[0][i]['name']
                sql_price = url[0][i]['price']
                sql_address = url[0][i]['address']
                sql_url = url[0][i]['url']
                sql_type_of = url[0][i]['type_of']
                sql_params = url[0][i]['params']
                sql_city = url[1][0]
                sql_chat = url[1][1]
                sql_urls_id = url[1][2]

                price_history = []
                price_now = [str(date_and_time), str(sql_price)]

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=? AND city =?', (sql_avito_id, sql_city))
                item_id = cur.fetchall()

                if item_id == [(sql_avito_id,)]:
                    cur.execute('SELECT price FROM offers WHERE avito_id=? AND city =?', (sql_avito_id, sql_city))


                    item_price = cur.fetchall()
                    old_price = item_price[0][0]

                    cur.execute('SELECT price_history FROM offers WHERE avito_id=? AND city =?',
                                (sql_avito_id, sql_city))
                    price_history = json.loads(cur.fetchall()[0][0])

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    price_history_srt = ''

                    if len(price_history) > 0:
                        for i in range(0, len(price_history), 2):
                            if i != 0 and i != 1:
                                percent_price_history = calculation_percent(price_history[i + 1], price_history[i - 1])
                                price_history_srt = price_history_srt + 'Дата: ' + price_history[i][
                                                                                   0:10] + '  Цена: ' + num_conversion(
                                    price_history[i + 1]) + ' руб.  (' + percent_price_history + '%)\n'

                            else:
                                price_history_srt = price_history_srt + 'Дата: ' + price_history[i][
                                                                                   0:10] + '  Цена: ' + num_conversion(
                                    price_history[i + 1]) + ' руб.\n'

                        difference_price = calculation_different_price(price_history[1], price_now[1])
                        percent_difference_price = calculation_percent_different_price(price_history[1], price_now[1])

                    if item_price == [(sql_price,)]:
                        cur.execute("UPDATE offers SET status=1, updated_date=?,urls_id=?, type_of=?, params=? WHERE avito_id=? AND city =?",
                                    (str(date_and_time),sql_urls_id, sql_type_of,sql_params, sql_avito_id, sql_city))
                        continue
                    else:
                        send_mes_to_bot(item_price, sql_chat, sql_avito_id, old_price, sql_price, price_history_srt,
                                        difference_price, percent_difference_price, sql_address, sql_url, sql_params,
                                        sql_type_of, 'update')

                        cur.execute(
                            "UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1, urls_id=?, type_of=?, params=? WHERE avito_id=? AND city =?",
                            (sql_price, old_price, str(date_and_time), str(price_history_dumps),sql_urls_id, sql_type_of,sql_params, sql_avito_id,
                             sql_city))
                        print('Price update | ' + str(sql_avito_id))
                        time.sleep(5)

                else:
                    send_mes_to_bot(item_price, sql_chat, sql_avito_id, old_price, sql_price, price_history_srt,
                                    difference_price, percent_difference_price, sql_address, sql_url, sql_params,
                                    sql_type_of, 'new')
                    print('No ID -> New Offer | ' + str(sql_avito_id))

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    cur.execute(
                        "INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url','created_date','updated_date','status','city','urls_id','type_of','params') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url,
                         str(date_and_time), str(date_and_time), 1, sql_city,sql_urls_id, sql_type_of, sql_params))
                    time.sleep(5)
    conn.commit()
    conn.close()


def get_urls():
    conn = sqlite3.connect(route_db)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT id,name,city,chatid FROM urls')
        urls = cur.fetchall()
        return urls
