import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import io

# 1. BOT TOKEN
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchi holati
user_mode = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('Insta link 🔗', 'Voice message 🎤', 'Qo\'lda yozilgan matn ✍️', 'Dollar kursi 💵', 'Ob-havo ☁️')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_mode[message.chat.id] = None
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bot qayta yuklandi. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ['Insta link 🔗', 'Voice message 🎤', 'Qo\'lda yozilgan matn ✍️', 'Dollar kursi 💵', 'Ob-havo ☁️'])
def buttons(message):
    user_mode[message.chat.id] = message.text
    if message.text == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram linkini tashlang 🔗")
    elif message.text == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Matn yuboring 🎤")
    elif message.text == 'Dollar kursi 💵':
        get_currency(message)
    elif message.text == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "🌤 Andijon: +28°C")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    mode = user_mode.get(message.chat.id)
    
    if 'instagram.com' in message.text:
        download_insta(message)
    elif mode == 'Voice message 🎤':
        make_voice(message)
    else:
        bot.send_message(message.chat.id, "Kerakli bo'limni tanlang!", reply_markup=main_menu())

# --- OVOZNI TUZATISH ---
def make_voice(message):
    try:
        # Xotira orqali yuborish (Eng xavfsiz yo'l)
        tts = gTTS(text=message.text, lang='uz')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        fp.name = 'voice.mp3' # Railway uchun nom shart
        bot.send_voice(message.chat.id, fp, caption="Tayyor! ✅")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ovozda xato: {str(e)}")

# --- INSTAGRAMNI TUZATISH ---
def download_insta(message):
    wait = bot.send_message(message.chat.id, "Qidirilmoqda... ⏳")
    try:
        # Bu API barqarorroq (SnapInsta alternatividan foydalanamiz)
        link = message.text.strip().split('?')[0] # Linkni tozalash
        api_url = f"https://api.vyturex.com/instadl?url={link}"
        res = requests.get(api_url, timeout=20).json()
        
        if res.get('video_url'):
            bot.send_video(message.chat.id, res['video_url'], caption="Video yuklandi! ✅")
            bot.delete_message(message.chat.id, wait.message_id)
        else:
            bot.edit_message_text("Video topilmadi yoki API band. ❌", message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"Xatolik: API hozirda ishlamayapti.", message.chat.id, wait.message_id)

def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {res[0]['Rate']} so'm")
    except:
        bot.send_message(message.chat.id, "Kursda xato!")

bot.infinity_polling()