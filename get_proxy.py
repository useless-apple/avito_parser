# coding=utf-8
import sqlite3

import requests


from requests import get
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError, ReadTimeout, SSLError, ConnectionError

from settings import route_db

ip_list = []


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
        cur.execute('SELECT * FROM proxy WHERE ip=?', (ip,))
        ip_sql = cur.fetchall()
        if len(ip_sql) > 0:
            if ip != ip_sql[0][1]:
                cur.execute(
                    "INSERT OR IGNORE INTO proxy ('ip') VALUES (?)",
                    (ip,))
        else:
            cur.execute(
                "INSERT OR IGNORE INTO proxy ('ip') VALUES (?)",
                (ip,))
    conn.commit()
    conn.close()


def get_ip_db():
    conn = sqlite3.connect(route_db)
    cur = conn.cursor()
    cur.execute('SELECT ip FROM proxy ORDER BY ROWID ASC LIMIT 1')
    ip = cur.fetchall()
    conn.commit()
    conn.close()
    if len(ip) == 0:
        get_proxy()
        ip = get_ip_db()
    return ip[0]


def delete_ip_db(ip):
    conn = sqlite3.connect(route_db)
    cur = conn.cursor()
    cur.execute('DELETE FROM proxy WHERE ip=?', (ip,))
    print()
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
    proxy_success = False
    while proxy_success == False:
        ip = get_ip_db()
        print('Получили IP: ' + ip[0])
        try:
            print('Trying: ' + ip[0])
            html = response_sucsess(url, ip[0], headers)
            if html is not None: return html[0]
        except (ProxyError, ConnectionError, ReadTimeout, SSLError):
            print('Delete proxy error: ' + ip[0])
            delete_ip_db(ip[0])


def response_sucsess(url, ip, headers):
    r = get(url, proxies={"https": ip}, headers=headers)
    if r.status_code == 200:
        if len(r.text) > 80000:
            print('IP Success')
            proxy_success = True
            return r, proxy_success
        else:
            print('Delete (len not enough: ' + ip)
            delete_ip_db(ip)

    else:
        print('Delete status cote not 200: ' + ip)
        delete_ip_db(ip)
