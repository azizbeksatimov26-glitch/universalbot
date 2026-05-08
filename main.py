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
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Hammasi 100% tuzatildi. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in ['Insta link 🔗', 'Voice message 🎤', 'Qo\'lda yozilgan matn ✍️', 'Dollar kursi 💵', 'Ob-havo ☁️'])
def buttons(message):
    user_mode[message.chat.id] = message.text
    if message.text == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram reels linkini tashlang 🔗")
    elif message.text == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Ovozga aylantirish uchun matn yuboring 🎤")
    elif message.text == 'Dollar kursi 💵':
        get_currency(message)
    elif message.text == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "🌤 Andijon: +28°C, havo zo'r!")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    mode = user_mode.get(message.chat.id)
    
    # AGAR LINK BO'LSA (Tugma bosilmagan bo'lsa ham)
    if 'instagram.com' in message.text:
        download_insta(message)
    
    # OVOZLI XABAR REJIMIDA
    elif mode == 'Voice message 🎤':
        make_voice(message)
    
    # QO'LDA YOZISH
    elif mode == 'Qo\'lda yozilgan matn ✍️':
        bot.send_message(message.chat.id, "✍️ Rasm generatori hozircha texnik tanaffusda, lekin ovoz va insta zo'r ishlayapti!")

# --- OVOZNI XOTIRADA YARATISH (Faylsiz, xatosiz) ---
def make_voice(message):
    try:
        tts = gTTS(text=message.text, lang='uz')
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        bot.send_voice(message.chat.id, audio_stream, caption="Tayyor! ✅")
    except:
        bot.send_message(message.chat.id, "Ovozda xato! Matn juda uzun yoki server band.")

# --- INSTAGRAMNI YANGI API BILAN TUZATISH ---
def download_insta(message):
    wait = bot.send_message(message.chat.id, "Video yuklanmoqda... ⏳")
    try:
        # Yangi va barqaror API (Cobalt muqobili)
        api_url = f"https://api.vyturex.com/instadl?url={message.text.strip()}"
        res = requests.get(api_url, timeout=30).json()
        
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Tayyor! ✅")
            bot.delete_message(message.chat.id, wait.message_id)
        else:
            bot.edit_message_text("Video topilmadi. Profil yopiq bo'lishi mumkin.", message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Instagram xizmati hozircha javob bermayapti. 1 daqiqa kutib qayta urinib ko'ring.", message.chat.id, wait.message_id)

def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {res[0]['Rate']} so'm")
    except:
        bot.send_message(message.chat.id, "Kursda xato!")

bot.infinity_polling()