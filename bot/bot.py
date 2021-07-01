import telebot

from bot.settings import TG_TOKEN

#Токен Вашего бота телеграм
TOKEN = TG_TOKEN
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def text_handler(chat_id, text):
    bot.send_message(chat_id, text)

