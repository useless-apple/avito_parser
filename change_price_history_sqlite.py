import json
import sqlite3

conn = sqlite3.connect('test.db')
with conn:
    cur = conn.cursor()
    cur.execute('SELECT avito_id,price_history FROM offers')
    final_price_history = []
    items = cur.fetchall()
    for item in items:
        id = item[0]
        price_history = json.loads(item[1])
        if len(price_history) == 0:
            continue
        price_list = []
        price = {}
        for i in range(len(price_history)):
            if i % 2 == 1:
                price['price'] = price_history[i]
                price_list.append(price)
                price = {}
            if i % 2 == 0:
                price['data'] = price_history[i]
        sql_price_list = json.dumps(price_list)
        cur.execute("UPDATE offers SET price_history=? WHERE avito_id=?",(sql_price_list, id))
conn.commit()
conn.close()