import telebot
from telebot import types
import pyttsx3
import os
import uuid

# 1. BOT TOKEN
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchi rejimi
user_mode = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Voice message 🎤', 'Dollar kursi 💵', 'Ob-havo ☁️')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_mode[message.chat.id] = None
    bot.send_message(message.chat.id, f"Salom Nurbekjon! Ovozli tizim qayta tiklandi. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == 'Voice message 🎤')
def voice_start(message):
    user_mode[message.chat.id] = 'voice'
    bot.send_message(message.chat.id, "Matn yuboring, men uni ovozga aylantiraman! 🎤")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if user_mode.get(message.chat.id) == 'voice':
        # Ovoz yaratish boshlandi
        wait = bot.send_message(message.chat.id, "Ovoz yozilmoqda... ⏳")
        
        # Har bir foydalanuvchi uchun alohida nom bilan fayl yaratamiz
        file_name = f"voice_{uuid.uuid4().hex}.ogg"
        
        try:
            # Offline ovoz generatori (Internet talab qilmaydi)
            engine = pyttsx3.init()
            
            # Ovoz tezligi va balandligini sozlash
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            
            # Faylga saqlash
            engine.save_to_file(message.text, file_name)
            engine.runAndWait()
            
            # Telegramga yuborish
            with open(file_name, 'rb') as audio:
                bot.send_voice(message.chat.id, audio, caption="Tayyor! ✅")
            
            bot.delete_message(message.chat.id, wait.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"Xatolik yuz berdi: {str(e)}", message.chat.id, wait.message_id)
            
        finally:
            # Server xotirasini to'ldirmaslik uchun faylni o'chiramiz
            if os.path.exists(file_name):
                os.remove(file_name)
    else:
        bot.send_message(message.chat.id, "Tugmani bosing!", reply_markup=main_menu())

bot.infinity_polling()