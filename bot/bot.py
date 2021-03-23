import telebot

#Токен Вашего бота телеграм
TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def text_handler(text):
    chat_id = '-1001487777112'
    bot.send_message(chat_id, text)

