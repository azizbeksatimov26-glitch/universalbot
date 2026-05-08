import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

# 1. BOT TOKEN
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

# Holatlarni saqlash
user_mode = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Insta link 🔗")
    btn2 = types.KeyboardButton("Voice message 🎤")
    btn3 = types.KeyboardButton("Qo'lda yozilgan matn ✍️")
    btn4 = types.KeyboardButton("Dollar kursi 💵")
    btn5 = types.KeyboardButton("Ob-havo ☁️")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_mode[message.chat.id] = None
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bot qayta quvvatlantirildi! 🔥", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["Insta link 🔗", "Voice message 🎤", "Qo'lda yozilgan matn ✍️", "Dollar kursi 💵", "Ob-havo ☁️"])
def menu_handler(message):
    txt = message.text
    user_mode[message.chat.id] = txt
    if txt == "Voice message 🎤":
        bot.send_message(message.chat.id, "Ovozga aylantirish uchun matn yuboring 🎤")
    elif txt == "Qo'lda yozilgan matn ✍️":
        bot.send_message(message.chat.id, "Rasmga yozish uchun matn yuboring ✍️")
    elif txt == "Insta link 🔗":
        bot.send_message(message.chat.id, "Instagram linkini yuboring 🔗")
    elif txt == "Dollar kursi 💵":
        get_dollar(message)
    elif txt == "Ob-havo ☁️":
        bot.send_message(message.chat.id, "🌤 Andijon: +28°C, havo juda ajoyib!")

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    mode = user_mode.get(message.chat.id)
    
    if mode == "Voice message 🎤":
        text_to_voice(message)
    elif mode == "Qo'lda yozilgan matn ✍️":
        handwritten_text(message)
    elif mode == "Insta link 🔗" or 'instagram.com' in message.text:
        instagram_download(message)
    else:
        bot.send_message(message.chat.id, "Bo'limni tanlang!", reply_markup=main_menu())

# --- OVOZNI TUZATISH ---
def text_to_voice(message):
    fname = f"v_{uuid.uuid4().hex}.mp3"
    try:
        # Matn bo'sh emasligini tekshiramiz
        if len(message.text) < 1: return
        
        tts = gTTS(text=message.text, lang='uz')
        tts.save(fname)
        with open(fname, 'rb') as audio:
            bot.send_voice(message.chat.id, audio, caption="Tayyor! ✅")
    except Exception as e:
        bot.send_message(message.chat.id, "Ovoz yaratishda xato! (Server band bo'lishi mumkin)")
    finally:
        if os.path.exists(fname): os.remove(fname)

# --- INSTAGRAMNI TUZATISH ---
def instagram_download(message):
    if 'instagram.com' not in message.text:
        bot.send_message(message.chat.id, "Bu Instagram linki emas! ❌")
        return

    wait = bot.send_message(message.chat.id, "Video qidirilmoqda... ⏳")
    try:
        # Yangilangan va barqaror API (Alternativ API)
        url = f"https://api.vyturex.com/instadl?url={message.text.strip()}"
        res = requests.get(url, timeout=30).json()
        
        if res.get("video_url"):
            bot.send_video(message.chat.id, res["video_url"], caption="Video yuklab berildi! ✅")
            bot.delete_message(message.chat.id, wait.message_id)
        else:
            bot.edit_message_text("Video topilmadi. Profil yopiq bo'lishi mumkin yoki API hozir ishlamayapti.", message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Xatolik! API hozirda juda ko'p so'rov qabul qilmoqda. 1 daqiqa kutib urinib ko'ring.", message.chat.id, wait.message_id)

# --- QOLGAN FUNKSIYALAR ---
def handwritten_text(message):
    fname = f"h_{uuid.uuid4().hex}.png"
    try:
        img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 150), message.text, fill=(0, 0, 0))
        img.save(fname)
        with open(fname, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    except:
        bot.send_message(message.chat.id, "Rasmda xato!")
    finally:
        if os.path.exists(fname): os.remove(fname)

def get_dollar(message):
    try:
        data = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(x for x in data if x["Ccy"] == "USD")
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {usd['Rate']} so'm")
    except:
        bot.send_message(message.chat.id, "Kursda xato!")

bot.infinity_polling()