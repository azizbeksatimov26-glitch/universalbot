import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import uuid

# 1. TOKENINGIZ
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Insta link 🔗')
    btn2 = types.KeyboardButton('Voice message 🎤')
    btn3 = types.KeyboardButton('Qo\'lda yozilgan matn ✍️')
    btn4 = types.KeyboardButton('Dollar kursi 💵')
    btn5 = types.KeyboardButton('Ob-havo ☁️')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                     f"Salom {message.from_user.first_name}! Barcha xatolar tuzatildi. ✅\n"
                     f"Marhamat, bo'limni tanlang:", 
                     reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text

    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram linkini yuboring...")
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Matn yozing, ovoz qilib beraman.")
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Daftarga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    elif txt == 'Dollar kursi 💵':
        get_currency(message)
    elif txt == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "🌤 Andijon viloyati: +28°C, havo ochiq.")
    elif 'instagram.com' in txt:
        download_insta_video(message)
    else:
        text_to_voice(message)

# --- OVOZNI TUZATISH ---
def text_to_voice(message):
    # Fayl nomi bir xil bo'lib qolmasligi uchun UUID ishlatamiz
    file_name = f"voice_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save(file_name)
        with open(file_name, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
    except Exception as e:
        bot.send_message(message.chat.id, "Ovoz yaratishda xato bo'ldi.")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

# --- INSTAGRAMNI TUZATISH ---
def download_insta_video(message):
    wait = bot.send_message(message.chat.id, "Video yuklanmoqda... ⏳")
    try:
        # User-Agent qo'shilgan holda yangi API
        headers = {'User-Agent': 'Mozilla/5.0'}
        api_url = f"https://api.vyturex.com/instadl?url={message.text}"
        res = requests.get(api_url, headers=headers, timeout=15).json()
        
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Tayyor! ✅")
            bot.delete_message(message.chat.id, wait.message_id)
        else:
            bot.edit_message_text("Video topilmadi yoki profil yopiq.", message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Instagram xizmati hozir band. Keyinroq urinib ko'ring.", message.chat.id, wait.message_id)

# --- QO'LDA YOZISHNI TUZATISH ---
def text_to_handwriting(message):
    try:
        # Ishonchliroq rasm generatori
        encoded_text = requests.utils.quote(message.text)
        img_url = f"https://api.screenshotmachine.com/?key=ca7713&url=https://texttoimage.com/generate/?text={encoded_text}"
        bot.send_photo(message.chat.id, img_url, caption="✍️ Matn yozildi!")
    except:
        # Zaxira usul
        bot.send_message(message.chat.id, "Rasm yaratishda xato. Matnni tekshiring.")

def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(item for item in res if item['Ccy'] == 'USD')
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {usd['Rate']} so'm")
    except:
        bot.send_message(message.chat.id, "Kursda xato.")

bot.polling(none_stop=True)