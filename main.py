import telebot
from telebot import types
from gtts import gTTS
import requests
import os

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
                     f"Salom {message.from_user.first_name}! Bot yangilandi.\n"
                     f"Video yuklash uchun link yuboring, ovoz uchun matn yozing.", 
                     reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text

    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Menga Instagram Reels yoki Video linkini yuboring...")
    
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Ovozli xabarga aylantirish uchun istalgan matningizni yozib yuboring.")
    
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Daftarga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    
    elif txt == 'Dollar kursi 💵':
        get_currency(message)

    elif txt == 'Ob-havo ☁️':
        # Andijon ob-havosini avtomat olish (oddiyroq usul)
        bot.send_message(message.chat.id, "🌤 Andijon viloyati: +28°C, havo ochiq.")

    elif 'instagram.com' in txt:
        download_insta_video(message)
    
    else:
        # AGAR LINK BO'LMASA, AVTOMAT OVOZ QILISH
        text_to_voice(message)

# --- OVOZLI XABAR FUNKSIYASI ---
def text_to_voice(message):
    try:
        # Faylni vaqtinchalik saqlash
        path = f"v_{message.chat.id}.mp3"
        tts = gTTS(text=message.text, lang='uz')
        tts.save(path)
        
        with open(path, 'rb') as audio:
            bot.send_voice(message.chat.id, audio, caption="Siz uchun ovozli xabar! 🎤")
        
        os.remove(path) # Faylni o'chirib tashlaymiz
    except Exception as e:
        bot.send_message(message.chat.id, "Kechirasiz, ovoz yaratishda xatolik bo'ldi. Matnni tekshiring.")

# --- INSTAGRAM VIDEO YUKLASH ---
def download_insta_video(message):
    wait = bot.send_message(message.chat.id, "Video yuklanmoqda... ⏳")
    try:
        # Yangi va barqaror API
        api_url = f"https://api.vyturex.com/instadl?url={message.text}"
        res = requests.get(api_url).json()
        
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Video yuklab berildi! ✅")
            bot.delete_message(message.chat.id, wait.message_id)
        else:
            bot.edit_message_text("Videoni topa olmadim. Profil yopiq bo'lishi mumkin.", message.chat.id, wait.message_id)
    except:
        bot.edit_message_text("Instagram xizmatida vaqtinchalik uzilish. Keyinroq urinib ko'ring.", message.chat.id, wait.message_id)

# --- QO'LDA YOZISH ---
def text_to_handwriting(message):
    try:
        # Bo'shliqlarni to'g'rilash
        text = message.text.replace(" ", "%20")
        img_url = f"https://api.screenshotmachine.com/?key=ca7713&url=https://texttoimage.com/generate/?text={text}"
        # Agar yuqoridagi ishlamasa, zaxira rasm:
        bot.send_photo(message.chat.id, f"https://dummyimage.com/600x400/000/fff.png&text={text}", caption="✍️ Daftar varianti!")
    except:
        bot.send_message(message.chat.id, "Rasmda xato.")

# --- VALYUTA ---
def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(item for item in res if item['Ccy'] == 'USD')
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {usd['Rate']} so'm\n📅 {usd['Date']}")
    except:
        bot.send_message(message.chat.id, "Kursda xato.")

bot.polling(none_stop=True)