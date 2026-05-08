import telebot
from telebot import types
from gtts import gTTS
import requests
import os

# Tokeningizni shu yerga yozing
TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

# Tugmalar menyusi
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Insta link 🔗')
    btn2 = types.KeyboardButton('Voice message 🎤')
    btn3 = types.KeyboardButton('Qo\'lda yozilgan matn ✍️')
    btn4 = types.KeyboardButton('Dollar kursi 💵')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Kerakli bo'limni tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram video linkini yuboring...")
    
    elif message.text == 'Voice message 🎤':
        msg = bot.send_message(message.chat.id, "Ovozga aylantirish uchun matn yozing:")
        bot.register_next_step_handler(msg, text_to_voice)
    
    elif message.text == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Listga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    
    elif message.text == 'Dollar kursi 💵':
        get_currency(message)
    
    # Instagram linkini tekshirish
    elif 'instagram.com' in message.text:
        bot.send_message(message.chat.id, "Video yuklanmoqda, kuting...")
        # Bu yerda API orqali yuklash kodi bo'ladi (RapidAPI kabi xizmatlar kerak)
        bot.send_message(message.chat.id, "Instagram yuklash uchun tashqi API ulanishi lozim.")

# 1. Matnni ovozli qilish (gTTS)
def text_to_voice(message):
    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save("voice.ogg")
        with open("voice.ogg", 'rb') as voice:
            bot.send_voice(message.chat.id, voice)
        os.remove("voice.ogg")
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik yuz berdi!")

# 2. Qo'lda yozilgan matn (API orqali)
def text_to_handwriting(message):
    try:
        txt = message.text.replace(" ", "%20")
        img_url = f"https://py Whatsa.pythonanywhere.com/write/?text={txt}" # Namuna API
        bot.send_photo(message.chat.id, img_url, caption="Mana sizning matningiz!")
    except:
        bot.send_message(message.chat.id, "Rasm yaratishda xatolik!")

# 3. Dollar kursi
def get_currency(message):
    url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    response = requests.get(url).json()
    
    usd_rate = 0
    date = ""
    for item in response:
        if item['Ccy'] == 'USD':
            usd_rate = float(item['Rate'])
            date = item['Diff']
            break
    
    text = f"📅 Bugun: {message.date}\n\n"
    text += f"🇺🇸 1 Dollar = {usd_rate} so'm\n"
    text += f"🇺🇸 100 Dollar = {usd_rate * 100} so'm\n"
    text += f"\nO'zgarish: {date} so'm"
    
    bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)