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
