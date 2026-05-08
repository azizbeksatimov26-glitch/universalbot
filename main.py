import telebot
from telebot import types
from gtts import gTTS
import requests
import os

# 1. TOKENINGIZNI TEKSHIRIB KO'RING
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Men tayyorman. Matn yuborsangiz ovoz qilib beraman!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text

    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram video linkini yuboring, men uni yuklab beraman! 📥")
    
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Istalgan matnni yuboring, uni ovozli xabarga aylantiraman.")
    
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Listga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    
    elif txt == 'Dollar kursi 💵':
        get_currency(message)
    
    elif 'instagram.com' in txt:
        download_insta_video(message)
    
    else:
        # AGAR FOYDALANUVCHI SHUNCHAKI MATN YOZSA, AVTOMATIK OVOZGA AYLANTIRADI
        text_to_voice(message)

# --- FUNKSIYALAR ---

def text_to_voice(message):
    try:
        # O'zbek tilida ovozga aylantirish
        tts = gTTS(text=message.text, lang='uz')
        tts.save("voice.ogg")
        with open("voice.ogg", 'rb') as voice:
            bot.send_voice(message.chat.id, voice, caption="Mana sizning ovozli xabaringiz! ✅")
        os.remove("voice.ogg")
    except:
        bot.send_message(message.chat.id, "Ovoz yaratishda xatolik!")

def download_insta_video(message):
    msg = bot.send_message(message.chat.id, "Video yuklanmoqda, kuting... ⏳")
    try:
        # Instagram downloader API (Bepul va ochiq API)
        url = f"https://api.vyturex.com/instadl?url={message.text}"
        res = requests.get(url).json()
        video_url = res['video_url']
        bot.send_video(message.chat.id, video_url, caption="Video tayyor! 🎬")
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("Videoni yuklab bo'lmadi. Linkni tekshiring yoki keyinroq urinib ko'ring.", message.chat.id, msg.message_id)

def text_to_handwriting(message):
    try:
        encoded_text = requests.utils.quote(message.text)
        img_url = f"https://py Whatsa.pythonanywhere.com/write/?text={encoded_text}" 
        bot.send_photo(message.chat.id, img_url, caption="Mana, qo'lda yozilgan matn! ✍️")
    except:
        bot.send_message(message.chat.id, "Rasm yaratishda xatolik.")

def get_currency(message):
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        response = requests.get(url).json()
        usd = next(item for item in response if item['Ccy'] == 'USD')
        rate = float(usd['Rate'])
        bot.send_message(message.chat.id, f"🇺🇸 1 Dollar = {rate} so'm\n📅 Sana: {usd['Date']}")
    except:
        bot.send_message(message.chat.id, "Kursni olib bo'lmadi.")

bot.polling(none_stop=True)