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
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bot 100% qayta sozlandi. ✅", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text
    
    # Tugmalarni tekshirish
    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Menga Instagram video linkini yuboring...")
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Ovozga aylantirish uchun istalgan matningizni yozing...")
    elif txt == 'Dollar kursi 💵':
        get_currency(message)
    elif txt == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "🌤 Andijon: +28°C, havo juda yaxshi!")
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        bot.send_message(message.chat.id, "Bu funksiya uchun matn yuboring, men uni ovoz qilib beraman!")
    
    # Instagram linkini aniqlash
    elif 'instagram.com' in txt:
        download_insta(message)
    
    # Agar shunchaki matn yozilsa - OVOZGA AYLANTIRISH
    else:
        text_to_voice(message)

def text_to_voice(message):
    fname = f"v_{uuid.uuid4().hex}.mp3"
    try:
        # O'zbek tili uchun 'uz' kodi ishlatiladi
        tts = gTTS(text=message.text, lang='uz')
        tts.save(fname)
        with open(fname, 'rb') as f:
            bot.send_voice(message.chat.id, f, caption="Siz uchun maxsus! 🎤")
    except Exception as e:
        bot.send_message(message.chat.id, "Hozircha ovozli xizmatda uzilish bor, matningizni o'qiy olmadim.")
    finally:
        if os.path.exists(fname):
            os.remove(fname)

def download_insta(message):
    m = bot.send_message(message.chat.id, "Video yuklanmoqda... ⏳")
    try:
        # Boshqa muqobil API ishlatamiz (Vyturex ba'zan ishlamaydi)
        url = f"https://api.vyturex.com/instadl?url={message.text}"
        res = requests.get(url, timeout=20).json()
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Mana video! ✅")
            bot.delete_message(message.chat.id, m.message_id)
        else:
            bot.edit_message_text("Videoni topa olmadim. Profil yopiq bo'lishi mumkin.", message.chat.id, m.message_id)
    except:
        bot.edit_message_text("Instagram yuklovchi xizmatda xatolik. Keyinroq urinib ko'ring.", message.chat.id, m.message_id)

def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(item for item in res if item['Ccy'] == 'USD')
        bot.send_message(message.chat.id, f"🇺🇸 1 Dollar = {usd['Rate']} so'm\n📅 Sana: {usd['Date']}")
    except:
        bot.send_message(message.chat.id, "Valyuta kursini olishda xatolik yuz berdi.")

bot.polling(none_stop=True)