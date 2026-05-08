import telebot
from telebot import types
from gtts import gTTS
import requests
import os

# 1. BOT TOKENINGIZNI SHU YERGA YOZING
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
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
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bo'limni tanlang:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text

    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram video linkini yuboring...")
    
    elif txt == 'Voice message 🎤':
        msg = bot.send_message(message.chat.id, "Ovozga aylantirish uchun matn yozing:")
        bot.register_next_step_handler(msg, text_to_voice)
    
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Listga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    
    elif txt == 'Dollar kursi 💵':
        get_currency(message)
    
    # Agar foydalanuvchi shunchaki Instagram link yuborsa
    elif 'instagram.com' in txt:
        bot.send_message(message.chat.id, "Tez orada video yuklab berish funksiyasi to'liq ishga tushadi. Hozircha bazani sozlayapman!")

# --- FUNKSIYALAR ---

def text_to_voice(message):
    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save("voice.ogg")
        with open("voice.ogg", 'rb') as voice:
            bot.send_voice(message.chat.id, voice)
        os.remove("voice.ogg")
    except Exception as e:
        bot.send_message(message.chat.id, "Xatolik! Balki matn juda qisqadir.")

def text_to_handwriting(message):
    try:
        # Bu bepul API matnni listga yozilgan rasmga aylantiradi
        txt = message.text.replace(" ", "%20")
        img_url = f"https://py Whatsa.pythonanywhere.com/write/?text={txt}" 
        bot.send_photo(message.chat.id, img_url, caption="Mana, qo'lda yozilgan matn! ✍️")
    except:
        bot.send_message(message.chat.id, "Rasm yaratishda xatolik yuz berdi.")

def get_currency(message):
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        response = requests.get(url).json()
        
        usd_rate = next(item for item in response if item['Ccy'] == 'USD')
        rate = float(usd_rate['Rate'])
        
        msg_text = (f"📅 Bugungi sana: {usd_rate['Date']}\n\n"
                    f"🇺🇸 1 Dollar = {rate} so'm\n"
                    f"🇺🇸 100 Dollar = {rate * 100:,} so'm\n"
                    f"📈 O'zgarish: {usd_rate['Diff']} so'm")
        bot.send_message(message.chat.id, msg_text)
    except:
        bot.send_message(message.chat.id, "Kurs ma'lumotlarini olib bo'lmadi.")

# Botni to'xtovsiz ishlashi uchun
bot.polling(none_stop=True)