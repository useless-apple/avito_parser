import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import sqlite3
import cfscrape
from datetime import datetime
import json


from bot.bot import text_handler

main_url = 'https://www.avito.ru/orenburg/doma_dachi_kottedzhi/prodam-ASgBAgICAUSUA9AQ?f=ASgBAQECAUSUA9AQAUDYCCTKWc5ZAUXAExh7ImZyb20iOm51bGwsInRvIjoxNDY0OH0'

def write_csv(result):
    with open('file.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ser=,'])
        for item in result:
            writer.writerow( (item['avito_id'],
                              item['name'],
                              item['price'],
                              item['address'],
                              item['url']
                              ))

def write_sqlite3(result):
    conn = sqlite3.connect("/root/python/avito_parser/avito_list.db")
    with conn:
        cur = conn.cursor()
        cur.execute('UPDATE offers SET status=0')
        for i in range(0,len(result)):

                sql_avito_id = result[i]['avito_id']
                sql_name = result[i]['name']
                sql_price = result[i]['price']
                sql_address = result[i]['address']
                sql_url = result[i]['url']

                price_history = []
                price_now = [str(datetime.utcnow()), str(sql_price)]

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=?', (sql_avito_id,))
                item_id = cur.fetchall()

                if (item_id == [(sql_avito_id,)]):
                    #print('yes')

                    cur.execute('SELECT price FROM offers WHERE avito_id=?', (sql_avito_id,))
                    item_price = cur.fetchall()

                    cur.execute('SELECT price_history FROM offers WHERE avito_id=?', (sql_avito_id,))
                    price_history = json.loads(cur.fetchall()[0][0])
                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)

                    if(item_price == [(sql_price,)]):
                        #print('Price ok')
                        cur.execute("UPDATE offers SET status=1, updated_date=? WHERE avito_id=?", (str(datetime.utcnow()), sql_avito_id))
                        continue
                    else:
                        text_handler('Обновилась цена id ' + str(sql_avito_id) + '\n Старая цена = ' + str(item_price[0][0]) + ' руб. / Новая цена = ' + str(sql_price) + '\n\nАдрес: ' + str(sql_address) + ' руб.\n\nСсылка ' + str(sql_url))
                        cur.execute("UPDATE offers SET price=?, old_price=?, updated_date=?, price_history=?, status=1 WHERE avito_id=?",(sql_price, item_price[0][0], str(datetime.utcnow()), str(price_history_dumps), sql_avito_id))
                        print('Price update')
                        time.sleep(5)

                else:
                    text_handler('Новое объявление ' + str(sql_avito_id) + '\n\nЦена: '+ str(sql_price) + ' руб.' + '\n\nАдрес: ' + str(sql_address) + '\n\nСсылка ' + str(sql_url))
                    print('No ID -> New Offer')

                    price_history += price_now
                    price_history_dumps = json.dumps(price_history)
                    cur.execute(
                        "INSERT OR IGNORE INTO offers ('avito_id','name','price','price_history','address','url','created_date','updated_date','status') VALUES (?,?,?,?,?,?,?,?,?)",
                        (sql_avito_id, sql_name, sql_price, str(price_history_dumps), sql_address, sql_url, str(datetime.utcnow()), str(datetime.utcnow()), 1))
                    time.sleep(5)
    conn.commit()
    conn.close()

def get_session():
    session = requests.Session()
    session.headers = {
            'Host':'www.avito.ru',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)   Gecko/20100101 Firefox/69.0',
            'Accept':'text/html',
            'Accept-Language':'ru,en-US;q=0.5',
            'DNT':'1',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1',
            'Pragma':'no-cache',
            'Cache-Control':'no-cache'}
    return cfscrape.create_scraper(sess=session)


def clean(text):
    return text.replace('\t','').replace('\n','').strip()

def get_page_data(page_url):
    session = get_session()
    r = session.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('div',{"data-marker":"catalog-serp"})
    
    if (table):
        if (table.find('div', {"data-marker": "witcher/block"})):
            table.find('div', {"data-marker": "witcher/block"}).decompose()
    rows = table.find_all('div',{"data-marker":"item"})
    
    result = []
    for row in rows:
        avito_id = int(row.get('data-item-id'))
        name = clean(row.find('h3',{"class":"title-root-395AQ"}).text)
        price = int(clean(row.find('meta', {"itemprop": "price"}).get("content")))
        url = 'https://avito.ru' + row.find('a', {"class":"iva-item-sliderLink-2hFV_"}).get("href")
        address = clean(row.find('span', {"class":"geo-address-9QndR"}).text)
        item = {'avito_id':avito_id,'name':name,'price':price,'address':address,'url':url,}
        result.append(item)
    return result

def main(main_url):
    print(str(datetime.utcnow()))
    session = get_session()
    r=session.get(main_url + '&pmax=3500000&pmin=2500000&p=1')
    
    if r.status_code == 200:
        
        soup=BeautifulSoup(r.text, 'html.parser')
        count_page = soup.find_all('span',{"class":"pagination-item-1WyVp"})[-2].text
        result = []
        
        for i in range(1,int(count_page) +1):
            value = random.random()
            scaled_value = 1 + (value * (9 - 5))
            print('Parsing page# ' + str(i) + ' of ' + count_page)
            page_url = main_url + '&pmax=3500000&pmin=2500000&p=' + str(i)
            result+=get_page_data(page_url)
            time.sleep(scaled_value)
        #write_csv(result)
        write_sqlite3(result)
    else:
        print('Error:'+ str(r.status_code))

if __name__ == '__main__':
    main(main_url)
