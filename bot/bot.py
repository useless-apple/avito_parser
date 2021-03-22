import telebot

#main variables
TOKEN = "1763434220:AAHwjEuTltLljp6rTfGf0gLSBe-LUE7J5vU"
bot = telebot.TeleBot(TOKEN)
#handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Привет, когда я вырасту, я буду парсить заголовки с хабра')

@bot.message_handler(content_types=['text'])
def text_handler(text):
    #text = message.text.lower()
    chat_id = '-1001487777112'
    bot.send_message(chat_id, text)

