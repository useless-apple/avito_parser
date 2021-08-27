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
        percent_difference_price = '- ' + str(
            round(((int(price_old) - int(price_new)) / int(price_new)) * 100, 2))
    else:
        percent_difference_price = '+ ' + str(
            round(((int(price_new) - int(price_old)) / int(price_old)) * 100, 2))
    return percent_difference_price


def send_mes_to_bot(item_price, sql_chat, sql_avito_id, old_price, sql_price, price_history_srt, difference_price,
                    percent_difference_price, sql_address, sql_url, sql_params, sql_type_of, type_update):
    if type_update == 'update':
        if sql_type_of == 'Недвижимость':
            if item_price >= [(sql_price,)]:
                text_handler(sql_chat, 'Обновилась цена id ' + str(
                    sql_avito_id) + '  ' + emoji_down + emoji_down + emoji_top_green + '\n Старая цена = ' + str(
                    num_conversion(old_price)) + ' руб. / Новая цена = ' + str(
                    num_conversion(sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                    price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nАдрес: ' + str(
                    sql_address) + '\n\nСсылка ' + str(sql_url))
            else:
                text_handler(sql_chat, 'Обновилась цена id ' + str(
                    sql_avito_id) + '  ' + emoji_top + emoji_top + emoji_down_red + '\n Старая цена = ' + str(
                    num_conversion(item_price[0][0])) + ' руб. / Новая цена = ' + str(
                    num_conversion(sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                    price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nАдрес: ' + str(
                    sql_address) + '\n\nСсылка ' + str(sql_url))
        elif sql_type_of == 'Транспорт':
            if item_price >= [(sql_price,)]:
                text_handler(sql_chat, 'Обновилась цена id ' + str(
                    sql_avito_id) + '  ' + emoji_down + emoji_down + emoji_top_green + '\n Старая цена = ' + str(
                    num_conversion(old_price)) + ' руб. / Новая цена = ' + str(
                    num_conversion(sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                    price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nПараметры: ' + str(
                    sql_params) + '\n\nСсылка ' + str(sql_url))
            else:
                text_handler(sql_chat, 'Обновилась цена id ' + str(
                    sql_avito_id) + '  ' + emoji_top + emoji_top + emoji_down_red + '\n Старая цена = ' + str(
                    num_conversion(item_price[0][0])) + ' руб. / Новая цена = ' + str(
                    num_conversion(sql_price)) + ' руб.\n\nИзменения цен \n' + str(
                    price_history_srt) + '\nРазница: ' + difference_price + ' (' + percent_difference_price + '%)\n\nПараметры: ' + str(
                    sql_params) + '\n\nСсылка ' + str(sql_url))
        else:
            text_handler(sql_chat, 'NONETYPE ' + str(sql_avito_id))
    elif type_update == 'new':
        if sql_type_of == 'Недвижимость':
            text_handler(sql_chat, 'Новое объявление ' + str(sql_avito_id) + '\n\nЦена: ' + str(
                sql_price) + ' руб.' + '\n\nАдрес: ' + str(sql_address) + '\n\nСсылка ' + str(sql_url))
        elif sql_type_of == 'Транспорт':
            text_handler(sql_chat, 'Новое объявление ' + str(sql_avito_id) + '\n\nЦена: ' + str(
                sql_price) + ' руб.' + '\n\nПараметры: ' + str(sql_params) + '\n\nСсылка ' + str(sql_url))
    else:
        text_handler(sql_chat, 'NONETYPEUPDATE ' + str(sql_avito_id))
