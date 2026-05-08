import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import uuid

# 1. BOT TOKEN
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Insta link 🔗', 'Voice message 🎤', 'Qo\'lda yozilgan matn ✍️', 'Dollar kursi 💵', 'Ob-havo ☁️')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bot 0 dan sozlandi va tayyor. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text
    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Menga Instagram video linkini yuboring...")
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Ovozga aylantirish uchun biron matn yuboring...")
    elif txt == 'Dollar kursi 💵':
        try:
            res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            bot.send_message(message.chat.id, f"🇺🇸 1 USD = {res[0]['Rate']} so'm")
        except: bot.send_message(message.chat.id, "Kursda xatolik!")
    elif txt == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "🌤 Andijon: +28°C, havo juda yaxshi!")
    elif 'instagram.com' in txt:
        download_insta(message)
    else:
        # HAR QANDAY MATNNI AVTOMAT OVOZ QILISH
        text_to_voice(message)

def text_to_voice(message):
    # Fayl nomi band bo'lmasligi uchun vaqtinchalik nom
    fname = f"v_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save(fname)
        with open(fname, 'rb') as f:
            bot.send_voice(message.chat.id, f)
    except:
        bot.send_message(message.chat.id, "Ovoz yaratishda xato bo'ldi.")
    finally:
        if os.path.exists(fname): os.remove(fname)

def download_insta(message):
    m = bot.send_message(message.chat.id, "Video yuklanmoqda... ⏳")
    try:
        res = requests.get(f"https://api.vyturex.com/instadl?url={message.text}").json()
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Tayyor! ✅")
            bot.delete_message(message.chat.id, m.message_id)
        else:
            bot.edit_message_text("Video topilmadi.", message.chat.id, m.message_id)
    except:
        bot.edit_message_text("Instagram xizmati hozir ishlamayapti.", message.chat.id, m.message_id)

bot.polling(none_stop=True)