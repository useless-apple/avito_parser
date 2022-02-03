import telebot

from date_and_time import time_sleep
from settings import TG_TOKEN

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(content_types=['text'])
def text_handler(chat_id, text):
    bot.send_message(chat_id, text)
    time_sleep(5)