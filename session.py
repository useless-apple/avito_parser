import time
import cfscrape
import requests

from bs4 import BeautifulSoup
from bot.bot import text_handler
from helpers import get_random_time
from new_logging import log
from settings import EXEPTION_CHAT


def get_session():
    session = requests.Session()
    session.headers = {
        'Host': 'www.avito.ru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)   Gecko/20100101 Firefox/69.0',
        'Accept': 'text/html',
        'Accept-Language': 'ru,en-US;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'}
    return cfscrape.create_scraper(sess=session)


def get_soup_from_page(page_url, count_try):
    session = get_session()
    r = session.get(page_url)
    if r.status_code != 200 and count_try < 4:
        error_message = 'Error' + str(r.status_code) + ' Try № ' + str(count_try)
        text_handler(EXEPTION_CHAT, error_message)
        log.error(error_message)
        time.sleep(get_random_time())
        get_soup_from_page(page_url, count_try + 1)

    elif r.status_code == 403:
        error_message = 'Error' + str(r.status_code) + ' Exit'
        text_handler(EXEPTION_CHAT, error_message)
        log.error(error_message)
        exit()

    elif count_try > 4:
        error_message = 'Error' + str(r.status_code) + ' Try ended'
        text_handler(EXEPTION_CHAT, error_message)
        log.error(error_message)
        soup = None
        return soup

    soup = BeautifulSoup(r.text, 'html.parser')
    return soup