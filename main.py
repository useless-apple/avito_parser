import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import sqlite3
import cfscrape

from bot.bot import text_handler

#Указываем ссылку на запрос
main_url = 'https://www.avito.ru/orenburg/doma_dachi_kottedzhi/prodam-ASgBAgICAUSUA9AQ?f=ASgBAQECAUSUA9AQAUDYCCTKWc5ZAUXAExh7ImZyb20iOm51bGwsInRvIjoxNDY1Mn0'

#Если нужно сгенерировать файл CSV
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

#если делать по cron то путь к .db файлу должен быть полностью, иначе cron остановит скрипт.
def write_sqlite3(result):
    conn = sqlite3.connect("avito_list.db")
    with conn:
        cur = conn.cursor()
        for i in range(3):
                sql_avito_id = result[i]['avito_id']
                sql_name = result[i]['name']
                sql_price = result[i]['price']
                sql_address = result[i]['address']
                sql_url = result[i]['url']

                cur.execute('SELECT avito_id FROM offers WHERE avito_id=?', (sql_avito_id,))
                item_id = cur.fetchall()

                if (item_id == [(sql_avito_id,)]):
                    print('ID found')
                    cur.execute('SELECT price FROM offers WHERE avito_id=?', (sql_avito_id,))
                    #item_price = cur.fetchall()
                    get_page_data_item(sql_url)

                    if(item_price == [(sql_price,)]):
                        print('Price ok')
                        continue
                    else:
                        #text_handler('Обновилась цена id ' + str(sql_avito_id) + '\n Старая цена = ' + str(item_price[0][0]) + ' руб. / Новая цена = ' + str(sql_price) + ' руб.\n\nСсылка ' + str(sql_url))
                        cur.execute("UPDATE offers SET price=? WHERE avito_id=?", (sql_price, sql_avito_id))
                        print('Price update')
                        time.sleep(5)

                else:
                    #text_handler('Новое объявление ' + str(sql_avito_id) + '\n\nЦена: '+ str(sql_price) + ' руб.' + '\n\nАдрес: ' + str(sql_address) + '\n\nСсылка ' + str(sql_url))
                    print('No ID ' + str(sql_avito_id))
                    cur.execute("INSERT OR IGNORE INTO offers ('avito_id','name','price','address','url') VALUES (?,?,?,?,?)", (sql_avito_id, sql_name, sql_price, sql_address, sql_url))
                    print('New Offer')
                    get_page_data_item(sql_url)
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
    return text.replace('\t','').replace('\n','').replace('\xa0',' ').strip()

def get_page_data(page_url):
    session = get_session()
    r = session.get(page_url)
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

def get_page_data_item(sql_url):
    session = get_session()
    r = session.get(sql_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    item_page = soup.find('div', {"class": "item-view"})
    item_page_options = item_page.find_all('li',{"class":"item-params-list-item"})
    result_options = []
    for a in item_page_options:
        result_options.append(clean(a.text))


    item_page_text = item_page.find('div',{"itemprop":"description"}).text
    item_page_coordinatesX = item_page.find('div',{"class":"item-map-wrapper"}).get("data-map-lat")
    item_page_coordinatesY = item_page.find('div',{"class":"item-map-wrapper"}).get("data-map-lon")

    print(result_options)
    print(item_page_text)
    print(item_page_coordinatesX)
    print(item_page_coordinatesY)




def get_address_geo(coordinatesX,coordinatesY):

def main(main_url):
    session = get_session()
    #указываем доп фильтрацию по цене и для первого запроса страницу пагинации 1
    r=session.get(main_url + '&pmax=3500000&pmin=2500000&p=1')
    if r.status_code == 200:
        soup=BeautifulSoup(r.text, 'html.parser')
        count_page = soup.find_all('span',{"class":"pagination-item-1WyVp"})[-2].text
        result = []
        for i in range(1):
            value = random.random()
            scaled_value = 1 + (value * (9 - 5))
            print('Parsing page# ' + str(i) + ' of ' + count_page)
            #Для последующих страниц, пагинацию генерим
            page_url = main_url + '&pmax=3500000&pmin=2500000&p=' + str(i)
            result+=get_page_data(page_url)
            time.sleep(scaled_value)

        print(result)
        #write_csv(result)
        write_sqlite3(result)
    else:
        print('Error:'+ str(r.status_code))
        time.sleep(600)
        main(main_url)

if __name__ == '__main__':
    #main(main_url)
    get_address_geo("51.789981","55.047341")