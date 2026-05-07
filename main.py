from telebot import TeleBot
import os 
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Nima gap?")

bot.polling()