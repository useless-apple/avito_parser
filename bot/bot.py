import telebot

from bot.settings import TG_TOKEN

#Токен Вашего бота телеграм
TOKEN = "TG_TOKEN"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def text_handler(text):
    chat_id = '-1001487777112'
    bot.send_message(chat_id, text)

