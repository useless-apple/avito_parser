import re

from bot.bot import text_handler
from date_and_time import time_sleep
from new_logging import log
from session import get_soup_from_page
from settings import EXEPTION_CHAT
from sqlite import write_sqlite3
from text_converter import clean


# Получаем данные для каждого объявления
def get_item_data(rows, type_of):
    result = []
    for row in rows:
        avito_id = ''
        name = ''
        price = ''
        url = ''
        address = ''
        params = ''

        # ID Объявления
        try:
            avito_id = int(row.get('data-item-id'))
        except:
            avito_id = 'Не найден'

        # Название товара
        try:
            name = clean(row.find('h3', {"itemprop": "name"}).text)
        except:
            name = 'Не найден'

        # Цена товара
        try:
            price = int(clean(row.find('meta', {"itemprop": "price"}).get("content")))
        except:
            price = 'Не найден'

        # Ссылка на товар
        try:
            url = 'https://avito.ru' + row.find('a', {"itemprop": "url"}).get("href")
        except:
            url = 'Не найден'

        # Для товара типа "Недвижимость"
        if type_of == 'Недвижимость':
            # Адрес
            try:
                address = clean(row.find('div', {"data-marker": "item-address"}).div.span.span.text)
            except:
                address = 'Не найден'

        # Для товара типа "Транспорт"
        elif type_of == 'Транспорт':
            # Параметры авто
            try:
                params = clean(row.find('div', {"data-marker": "item-specific-params"}).text)
            except:
                params = 'Не найден'

            # Адрес
            try:
                address = clean(row.find('div', attrs={"class": re.compile(r"geo-georeferences")}).span.text)
            except:
                address = 'Не найден'

        elif type_of == 'Хобби и отдых':
            # Параметры объявления
            try:
                params = clean(row.find('div', attrs={"class": re.compile(r"iva-item-description")}).text)
            except:
                params = 'Не найден'

            # Адрес
            try:
                address = clean(row.find('span', attrs={"class": re.compile(r"geo-address")}).span.text)
            except:
                address = 'Не найден'
        item = {
            'avito_id': avito_id,
            'name': name,
            'price': price,
            'address': address,
            'url': url,
            'type_of': type_of,
            'params': params
        }
        result.append(item)
    return result


# Получаем таблицу с объявлениями
def get_page_rows(soup, type_of):
    table = soup.find('div', {"data-marker": "catalog-serp"})

    if table:  # Удаляем рекламные блоки
        if table.find('div', {"data-marker": "witcher/block"}):
            table.find('div', {"data-marker": "witcher/block"}).decompose()
        rows = table.find_all('div', {"data-marker": "item"})
        result = get_item_data(rows, type_of)

    else:
        error_message = 'Error not table' + str(soup) + str(table)
        log.error(error_message)
        text_handler(EXEPTION_CHAT, 'Error not table// Check LOGS')
        result = []
    return result


# Получаем страницу с объявлениями
def get_page_data(page_url, count_try):
    next_pagination = True
    soup = get_soup_from_page(page_url, count_try)
    if not soup[1]:
        error_message = 'Next parsing none ' + str(page_url)
        log.error(error_message)
        text_handler(EXEPTION_CHAT, error_message)
        return [], False

    if not soup[0]:
        error_message = 'Soup is None ' + str(page_url)
        log.error(error_message)
        text_handler(EXEPTION_CHAT, error_message)
        return [], False

    try:
        type_of = soup[0].find('div', {"data-marker": "breadcrumbs"}).find_all('span', {"itemprop": "itemListElement"})[
            1].find('a').text
    except:
        type_of = 'None Type'
        log.warn('type_of = None Type')

    if soup[0].find_all('div', attrs={"class": re.compile(r"items-items")}):
        if len(soup[0].find_all('div', attrs={"class": re.compile(r"items-items")})) > 1:
            log.warn('Found another offers | Break pagination ' + str(page_url))
            next_pagination = False
    try:
        result = get_page_rows(soup[0], type_of)
    except:
        result = None
        error_message = 'Error get_page_rows' + '\n ' + page_url
        text_handler(EXEPTION_CHAT, error_message)
        log.error(error_message)
    return result, next_pagination


# Получаем список страниц пагинации
def get_count_page(soup, url_task):
    try:
        pagination = soup.find('div', {"data-marker": "pagination-button"})
        pagination.find('span', {"data-marker": "pagination-button/prev"}).decompose()
        pagination.find('span', {"data-marker": "pagination-button/next"}).decompose()
        count_page = pagination.find_all('span')[-1].text
    except:
        count_page = 1
        error_message = 'Error pagination' + '\n ' + url_task
        text_handler(EXEPTION_CHAT, error_message)
        log.error(error_message)
    return count_page


# Получаем данные для одного задания (ссылки со всеми пагинациями)
def get_result_task(count_page, url_task):
    next_pagination = True
    result = []
    for i in range(1, int(count_page) + 1):
        if next_pagination:  # Проверяем нужно ли парсить следующие страницы
            log.info('Parsing page# ' + str(i) + ' of ' + str(count_page))
            page_url = url_task + '&p=' + str(i)
            try:
                page_data = get_page_data(page_url, 1)
            except:
                page_data = None, True
                error_message = 'Error get_page_data' + '\n ' + page_url
                text_handler(EXEPTION_CHAT, error_message)
                log.error(error_message)

            result += page_data[0]
            next_pagination = page_data[1]
            time_sleep()
        else:
            break
    return result


# Получаем глобальный результат по всем заданиям
def get_global_result(tasks):
    global_result = []
    for task in tasks:
        url_task = task[1]
        task = [task[2], task[3], task[0]]
        log.info('Url parsing ' + str(url_task))
        soup = get_soup_from_page(url_task + '&p=1', 1)
        count_page = get_count_page(soup[0], url_task)
        result = get_result_task(count_page, url_task)
        time_sleep()
        item = [result, task]
        write_sqlite3(item)
        global_result.append(item)
    return global_result
