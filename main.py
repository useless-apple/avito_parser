import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import sqlite3


main_url = 'https://www.avito.ru/orenburg/doma_dachi_kottedzhi/prodam/dom-ASgBAQICAUSUA9AQAUDYCBTOWQ?f=ASgBAQECAUSUA9AQAUDYCBTOWQFFwBMYeyJmcm9tIjpudWxsLCJ0byI6MTQ2NTF9'
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

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
    conn = sqlite3.connect("avito_list.db")
    with conn:
        cur = conn.cursor()
        for i in range(0,len(result)):
                sql_avito_id = result[i]['avito_id']
                sql_name = result[i]['name']
                sql_price = result[i]['price']
                sql_address = result[i]['address']
                sql_url = result[i]['url']

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=?', (sql_avito_id,))
                item_id = cur.fetchall()
                print(item_id)
                print(sql_avito_id)

                if (item_id == [(sql_avito_id,)]):
                    print('yes')

                    cur.execute('SELECT price FROM offers WHERE avito_id=?', (sql_avito_id,))
                    item_price = cur.fetchall()
                    if(item_price == [(sql_price,)]):
                        print('Price ok')
                        continue
                    else:
                        cur.execute("UPDATE offers SET price=? WHERE avito_id=?", (sql_price, sql_avito_id))
                        print('Price update')
                else:
                    print('No ID')
                    cur.execute("INSERT OR IGNORE INTO offers ('avito_id','name','price','address','url') VALUES (?,?,?,?,?)", (sql_avito_id, sql_name, sql_price, sql_address, sql_url))
                    print('New Offer')
    conn.commit()
    conn.close()

def clean(text):
    return text.replace('\t','').replace('\n','').strip()

def get_page_data(page_url):
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('div',{"data-marker":"catalog-serp"})
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
    r=requests.get(main_url + '?&pmax=4000000&s=1&user=1&p=1')
    print(main_url + '?p=1&pmax=4000000&s=1&user=1')
    if r.status_code == 200:
        soup=BeautifulSoup(r.text, 'html.parser')
        count_page = soup.find_all('span',{"class":"pagination-item-1WyVp"})[-2].text
        result = []
        for i in range(1,int(count_page) +1):
            value = random.random()
            scaled_value = 1 + (value * (9 - 5))
            print('Parsing page# ' + str(i) + ' of ' + count_page)
            page_url = main_url + '&pmax=4000000&s=1&user=1&p=' + str(i)
            print(page_url)
            result+=get_page_data(page_url)
            time.sleep(scaled_value)

        print(result)
        write_csv(result)
        write_sqlite3(result)
    else:
        print('Error:'+ str(r.status_code))
        time.sleep(600)
        main(main_url)

if __name__ == '__main__':
    main(main_url)