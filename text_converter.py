from bot.bot import text_handler

emoji_top = u'\U0001F4C8'
emoji_top_green = u'\U00002705'

emoji_down = u'\U0001F4C9'
emoji_down_red = u'\U0000274C'


def num_conversion(a):
    return '{:,}'.format(int(a))


# Отчищаем текст перед принятием
def clean(text):
    return text.replace('\t', '').replace('\n', '').strip()


# Расчитываем процент между новой и старой ценой (для истории)
def calculation_percent(price_old, price_new):
    if price_old > price_new:
        percent_price_history = '- ' + str(round(((int(price_old) - int(price_new)) / int(price_new)) * 100, 2))
    else:
        percent_price_history = '+ ' + str(round(((int(price_new) - int(price_old)) / int(price_old)) * 100, 2))
    return percent_price_history


# Расчитываем разницу между новой и старой ценой
def calculation_different_price(price_old, price_new):
    if price_old > price_new:
        difference_price = '- ' + str(num_conversion(int(price_old) - int(price_new)))

    else:
        difference_price = '+ ' + str(num_conversion(int(price_new) - int(price_old)))
    return difference_price


def send_mes_to_bot(item):
    from main import log

    first_row = ''  # ID
    second_row = ''  # Name
    third_row = ''  # price
    fours_row = ''  # price_history
    five_row = ''  # address
    six_row = ''  # params
    seven_row = ''  # url

    if item['type_update'] == 'update':
        if item['item_price'] >= [(item['sql_price'],)]:
            first_row = 'Обновилась цена id ' + str(item['sql_avito_id']) + '  ' + \
                        emoji_down + emoji_down + emoji_top_green + '\n\n'

            third_row = 'Старая цена = ' + str(num_conversion(item['old_price'])) + ' руб. / Новая цена = ' + \
                        str(num_conversion(item['sql_price'])) + ' руб.\n\n'
        else:
            first_row = 'Обновилась цена id ' + str(item['sql_avito_id']) + '  ' + \
                        emoji_top + emoji_top + emoji_down_red + '\n\n'

            third_row = 'Старая цена = ' + str(num_conversion(item['item_price'][0][0])) + ' руб. / Новая цена = ' + \
                        str(num_conversion(item['sql_price'])) + ' руб.\n\n'
        fours_row = 'Изменения цен \n' + str(item['price_history_srt']) + '\nРазница: ' + \
                    item['difference_price'] + ' (' + item['percent_difference_price'] + '%)\n\n'
    elif item['type_update'] == 'new':
        first_row = 'Новое объявление ' + str(item['sql_avito_id']) + '\n\n'
        third_row = 'Цена: ' + str(item['sql_price']) + ' руб.\n\n'
    else:
        log.error('type_update = NONETYPE ' + str(item['sql_avito_id']))
    second_row = str(item['sql_name']) + '\n\n'
    five_row = 'Адрес: ' + str(item['sql_address']) + '\n\n'
    six_row = 'Параметры: ' + str(item['sql_params']) + '\n\n'
    seven_row = 'Ссылка ' + str(item['sql_url']) + '\n\n'
    none_type_of = ['Личные вещи', 'Работа', 'Для дома и дачи', 'Предложение услуг', 'Электроника', 'Животные', 'Готовый бизнес и оборудование']
    if item['sql_type_of'] == 'Недвижимость':
        mes_to_bot = first_row + third_row + fours_row + five_row + seven_row
    elif item['sql_type_of'] == 'Транспорт':
        mes_to_bot = first_row + second_row + third_row + fours_row + six_row + seven_row
    elif item['sql_type_of'] == 'Хобби и отдых':
        mes_to_bot = first_row + second_row + third_row + fours_row + five_row + six_row + seven_row
    elif item['sql_type_of'] in none_type_of:
        mes_to_bot = first_row + second_row + third_row + fours_row + seven_row
    else:
        log.error('sql_type_of = NONETYPE ' + str(item['sql_avito_id']))
        mes_to_bot = 'sql_type_of = NONETYPE ' + str(item['sql_avito_id'])
    text_handler(item['sql_chat'], mes_to_bot)


def parse_items_to_send(items):
    for item in items:
        send_mes_to_bot(item)
