# coding=utf-8
import sqlite3

import requests
from requests import get
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError, ReadTimeout, SSLError, ConnectionError

from main import write_json_txt, route_db

ip_list = []
url = 'https://www.avito.ru/orenburg/doma_dachi_kottedzhi/prodam-ASgBAgICAUSUA9AQ?f=ASgBAQECAUSUA9AQAUDYCCTKWc5ZAUXAExh7ImZyb20iOm51bGwsInRvIjoxNDY0OH0&pmax=3500000&pmin=2500000'


# Получает прокси
def get_proxy():
    url = "https://www.sslproxies.org/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find("tbody").find_all("tr")
    for element in elements:
        ip = element.find_all("td")[0].text
        port = element.find_all("td")[1].text
        proxy = "http://{}:{}".format(ip, port)
        ip_list.append(proxy)
    write_json_txt(ip_list)
    write_sqlite3_proxy(ip_list)

def write_sqlite3_proxy(ip_list):
    conn = sqlite3.connect(route_db)
    for ip in ip_list:
        cur = conn.cursor()
        cur.execute('SELECT * FROM proxy WHERE ip=?', (ip, ))
        ip_sql = cur.fetchall()
        if len(ip_sql)>0:
            if ip != ip_sql[0][1]:
                cur.execute(
                    "INSERT OR IGNORE INTO proxy ('ip') VALUES (?)",
                    (ip, ))
        else:
            cur.execute(
                "INSERT OR IGNORE INTO proxy ('ip') VALUES (?)",
                (ip,))
    conn.commit()
    conn.close()

def get_ip_db():
    conn = sqlite3.connect(route_db)
    cur = conn.cursor()
    cur.execute('SELECT ip FROM proxy')
    ip_list = cur.fetchall()
    conn.commit()
    conn.close()
    return ip_list

def delete_ip_db(ip):
    conn = sqlite3.connect(route_db)
    cur = conn.cursor()
    cur.execute('DELETE FROM proxy WHERE ip=?', (ip, ))
    conn.commit()
    conn.close()


# Продбирает proxy
def get_html(url):
    headers = {
        'Host': 'www.avito.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)   Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html',
        'Accept-Language': 'ru,en-US;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'}
    ip_list = get_ip_db()
    if len(ip_list) <= 0:
        print(len(ip_list))
        get_proxy()
        get_ip_db()
    for ip in ip_list:
        print(ip)
        try:
            html = response_sucsess(url, ip[0], headers)
            if html is not None: return html
        except (ProxyError, ConnectionError, ReadTimeout, SSLError):
            ip_list.pop(ip_list.index(ip))
            delete_ip_db(ip[0])
            print('delete')
            continue


def response_sucsess(url, ip, headers):
    r = get(url, proxies={"https": ip}, headers=headers, timeout=7)
    if r.status_code == 200:
        if len(r.text) > 80000:
            print(r.text)
            return r.text
        else:
            delete_ip_db(ip[0])
            print('delete')
    else:
        delete_ip_db(ip[0])
        print('delete')



if __name__ == '__main__':
    #get_proxy()
    get_html(url)
