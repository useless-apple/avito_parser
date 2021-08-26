import sqlite3
import json
import time
from datetime import datetime

from settings import route_db
from bot.bot import text_handler
from text_converter import num_conversion, calculation_percent, calculation_different_price, calculation_percent_different_price

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

                    cur.execute('SELECT price_history FROM offers WHERE avito_id=? AND city =?',(sql_avito_id, url[1][0]))
                    price_history = json.loads(cur.fetchall()[0][0])

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    price_history_srt = ''

                    if len(price_history) > 0:
                        for i in range(0, len(price_history), 2):
                            if i != 0 and i != 1:
                                percent_price_history = calculation_percent(price_history[i + 1], price_history[i - 1])
                                price_history_srt = price_history_srt + 'Дата: ' + price_history[i][0:10] + '  Цена: ' + num_conversion(price_history[i + 1]) + ' руб.  (' + percent_price_history + '%)\n'

                            else:
                                price_history_srt = price_history_srt + 'Дата: ' + price_history[i][0:10] + '  Цена: ' + num_conversion(price_history[i + 1]) + ' руб.\n'

                        difference_price = calculation_different_price(price_history[1], price_now[1])
                        percent_difference_price = calculation_percent_different_price(price_history[1], price_now[1])

                    if item_price == [(sql_price,)]:
                        cur.execute("UPDATE offers SET status=1, updated_date=? WHERE avito_id=? AND city =?",(str(datetime.utcnow()), sql_avito_id, url[1][0]))
                        continue
                    else:
                        if item_price >= [(sql_price,)]:
                            text_handler(url[1][1], 'Обновилась цена id ' + str(
                                sql_avito_id) + '  ' + emoji_down + emoji_down + emoji_top_green + '\n Старая цена = ' + str(
                                num_conversion(item_price[0][0])) + ' руб. / Новая цена = ' + str(num_conversion(
                                sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                                price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nАдрес: ' + str(
                                sql_address) + '\n\nСсылка ' + str(sql_url))
                        else:
                            text_handler(url[1][1], 'Обновилась цена id ' + str(
                                sql_avito_id) + '  ' + emoji_top + emoji_top + emoji_down_red + '\n Старая цена = ' + str(
                                num_conversion(item_price[0][0])) + ' руб. / Новая цена = ' + str(num_conversion(
                                sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                                price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nАдрес: ' + str(
                                sql_address) + '\n\nСсылка ' + str(sql_url))

                        cur.execute(
                            "UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1 WHERE avito_id=? AND city =?",
                            (sql_price, item_price[0][0], str(datetime.utcnow()), str(price_history_dumps), sql_avito_id, url[1][0]))
                        print('Price update' + str(sql_avito_id))
                        time.sleep(5)

                else:
                    text_handler(url[1][1], 'Новое объявление ' + str(sql_avito_id) + '\n\nЦена: ' + str(
                        sql_price) + ' руб.' + '\n\nАдрес: ' + str(sql_address) + '\n\nСсылка ' + str(sql_url))
                    print('No ID -> New Offer' + str(sql_avito_id))

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    cur.execute("INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url','created_date','updated_date','status','city') VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url,str(datetime.utcnow()), str(datetime.utcnow()), 1, url[1][0]))
                    time.sleep(5)
    conn.commit()
    conn.close()


def get_urls():
    conn = sqlite3.connect(route_db)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT name,city,chatid FROM urls')
        urls = cur.fetchall()
        return urls
