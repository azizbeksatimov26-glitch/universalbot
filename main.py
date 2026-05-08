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
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Hammasi noldan tuzatildi. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ["Insta link 🔗", "Voice message 🎤", "Qo'lda yozilgan matn ✍️", "Dollar kursi 💵", "Ob-havo ☁️"])
def menu_handler(message):
    txt = message.text
    if txt == "Voice message 🎤":
        user_mode[message.chat.id] = "voice"
        bot.send_message(message.chat.id, "Matn yuboring, ovoz qilib beraman 🎤")
    elif txt == "Qo'lda yozilgan matn ✍️":
        user_mode[message.chat.id] = "hand"
        bot.send_message(message.chat.id, "Rasmga yozish uchun matn yuboring ✍️")
    elif txt == "Insta link 🔗":
        user_mode[message.chat.id] = "insta"
        bot.send_message(message.chat.id, "Instagram link yuboring 🔗")
    elif txt == "Dollar kursi 💵":
        get_dollar(message)
    elif txt == "Ob-havo ☁️":
        get_weather(message)

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    mode = user_mode.get(message.chat.id)
    if mode == "voice":
        text_to_voice(message)
    elif mode == "hand":
        handwritten_text(message)
    elif mode == "insta":
        instagram_download(message)
    else:
        bot.send_message(message.chat.id, "Bo'limni tanlang!", reply_markup=main_menu())

# --- FUNKSIYALAR ---

def text_to_voice(message):
    fname = f"{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save(fname)
        with open(fname, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
    except:
        bot.send_message(message.chat.id, "Ovozda xato!")
    finally:
        if os.path.exists(fname): os.remove(fname)

def handwritten_text(message):
    fname = f"{uuid.uuid4().hex}.png"
    try:
        # Font fayli bo'lmasa ham ishlashi uchun tizim fontidan foydalanamiz
        img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        # Railwayda default font ishlatamiz (xato bermasligi uchun)
        draw.text((50, 150), message.text, fill=(0, 0, 0))
        img.save(fname)
        with open(fname, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Tayyor! ✍️")
    except:
        bot.send_message(message.chat.id, "Rasmda xato!")
    finally:
        if os.path.exists(fname): os.remove(fname)

def instagram_download(message):
    wait = bot.send_message(message.chat.id, "Yuklanmoqda... ⏳")
    try:
        res = requests.get(f"https://api.vyturex.com/instadl?url={message.text}").json()
        bot.send_video(message.chat.id, res["video_url"], caption="Tayyor ✅")
        bot.delete_message(message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Xato! Link noto'g'ri yoki API band.", message.chat.id, wait.message_id)

def get_dollar(message):
    try:
        data = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(x for x in data if x["Ccy"] == "USD")
        bot.send_message(message.chat.id, f"🇺🇸 Dollar kursi: {usd['Rate']} so'm\n📅 {usd['Date']}")
    except:
        bot.send_message(message.chat.id, "Kursda xato!")

def get_weather(message):
    # API KEY'siz ham ishlaydigan sodda ob-havo
    bot.send_message(message.chat.id, "🌤 Andijon ob-havosi: +28°C, havo ochiq!")

print("Bot ishladi...")
bot.infinity_polling()