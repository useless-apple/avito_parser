# coding=utf-8
import sqlite3

import requests
from requests import get
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError, ReadTimeout, SSLError, ConnectionError


ip_list = []

route_db = "avito_database.db"

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
    print(ip)
    cur.execute('DELETE FROM proxy WHERE ip=?', (ip, ))
    conn.commit()
    conn.close()


# Продбирает proxy
def get_html1(url):
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
    print(ip_list)
    if len(ip_list) <= 0:
        print(len(ip_list))
        get_proxy()
        ip_list = get_ip_db()
    for ip in ip_list:
        try:
            print('Trying: ' + ip[0])
            html = response_sucsess(url, ip[0], headers)
            if html is not None: return html
        except (ProxyError, ConnectionError, ReadTimeout, SSLError):
            delete_ip_db(ip[0])
            print('Delete proxy error: ' + ip[0])
            continue


def response_sucsess(url, ip, headers):
    print('response ip ' + ip)
    r = get(url, proxies={"https": ip}, headers=headers, timeout=7)
    if r.status_code == 200:
        if len(r.text) > 80000:
            print('IP Success')
            return r
        else:
            delete_ip_db(ip)
            print('Delete (len not enough: ' + ip)
    else:
        delete_ip_db(ip)
        print('Delete status cote not 200: ' + ip)


