from bot.bot import text_handler

emoji_top = u'\U0001F4C8'
emoji_top_green = u'\U00002705'

emoji_down = u'\U0001F4C9'
emoji_down_red = u'\U0000274C'


def num_conversion(a):
    return '{:,}'.format(int(a))


def clean(text):
    return text.replace('\t', '').replace('\n', '').strip()


def calculation_percent(price_old, price_new):
    if price_old > price_new:
        percent_price_history = '+ ' + str(round(((int(price_old) - int(price_new)) / int(price_new)) * 100, 2))
    else:
        percent_price_history = '- ' + str(round(((int(price_new) - int(price_old)) / int(price_old)) * 100, 2))
    return percent_price_history


def calculation_different_price(price_old, price_new):
    if price_old > price_new:
        difference_price = '- ' + str(num_conversion(int(price_old) - int(price_new)))

    else:
        difference_price = '+ ' + str(num_conversion(int(price_new) - int(price_old)))
    return difference_price


def calculation_percent_different_price(price_old, price_new):
    if price_old > price_new:
        percent_difference_price = '- ' + \
                                   str(round(((int(price_old) - int(price_new)) / int(price_new)) * 100, 2))
    else:
        percent_difference_price = '+ ' + \
                                   str(round(((int(price_new) - int(price_old)) / int(price_old)) * 100, 2))
    return percent_difference_price


def send_mes_to_bot(item_price, sql_chat, sql_avito_id, sql_name, old_price, sql_price, price_history_srt,
                    difference_price,
                    percent_difference_price, sql_address, sql_url, sql_params, sql_type_of, type_update):
    from main import log

    first_row = ''  # ID
    second_row = ''  # Name
    third_row = ''  # price
    fours_row = ''  # price_history
    five_row = ''  # address
    six_row = ''  # params
    seven_row = ''  # url

    if type_update == 'update':
        if item_price >= [(sql_price,)]:
            first_row = 'Обновилась цена id ' + str(sql_avito_id) + '  ' + \
                        emoji_down + emoji_down + emoji_top_green + '\n\n'

            third_row = 'Старая цена = ' + str(num_conversion(old_price)) + ' руб. / Новая цена = ' + \
                        str(num_conversion(sql_price)) + ' руб.\n\n'
        else:
            first_row = 'Обновилась цена id ' + str(sql_avito_id) + '  ' + \
                        emoji_top + emoji_top + emoji_down_red + '\n\n'

            third_row = 'Старая цена = ' + str(num_conversion(item_price[0][0])) + ' руб. / Новая цена = ' + \
                        str(num_conversion(sql_price)) + ' руб.\n\n'
        fours_row = 'Изменения цен \n' + str(price_history_srt) + '\nРазница: ' + \
                    difference_price + ' (' + percent_difference_price + '%)\n\n'
    elif type_update == 'new':
        first_row = 'Новое объявление ' + str(sql_avito_id) + '\n\n'
        third_row = 'Цена: ' + str(sql_price) + ' руб.\n\n'
    else:
        log.error('type_update = NONETYPE ' + str(sql_avito_id))
    second_row = str(sql_name) + '\n\n'
    five_row = 'Адрес: ' + str(sql_address) + '\n\n'
    six_row = 'Параметры: ' + str(sql_params) + '\n\n'
    seven_row = 'Ссылка ' + str(sql_url) + '\n\n'

    if sql_type_of == 'Недвижимость':
        mes_to_bot = first_row + third_row + fours_row + five_row + seven_row
    elif sql_type_of == 'Транспорт':
        mes_to_bot = first_row + second_row + third_row + fours_row + six_row + seven_row
    elif sql_type_of == (
            'Личные вещи' or 'Работа' or 'Для дома и дачи' or 'Предложение услуг' or 'Хобби и отдых' or 'Электроника' or 'Животные' or 'Готовый бизнес и оборудование'):
        mes_to_bot = first_row + second_row + third_row + fours_row + seven_row
    else:
        log.error('sql_type_of = NONETYPE ' + str(sql_avito_id))
        mes_to_bot = 'sql_type_of = NONETYPE ' + str(sql_avito_id)
    text_handler(sql_chat, mes_to_bot)
