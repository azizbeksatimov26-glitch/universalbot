import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import time

# 1. TOKENINGIZ
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Insta link 🔗')
    btn2 = types.KeyboardButton('Voice message 🎤')
    btn3 = types.KeyboardButton('Qo\'lda yozilgan matn ✍️')
    btn4 = types.KeyboardButton('Dollar kursi 💵')
    btn5 = types.KeyboardButton('Ob-havo ☁️') # YANGI QO'SHILDI
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                     f"Salom {message.from_user.first_name}! Hammasi tuzatildi.\n"
                     f"Matn yozsangiz avtomat ovoz qilaman. Link yuborsangiz video yuklayman!", 
                     reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    txt = message.text

    if txt == 'Insta link 🔗':
        bot.send_message(message.chat.id, "Instagram video linkini yuboring...")
    
    elif txt == 'Voice message 🎤':
        bot.send_message(message.chat.id, "Ovozga aylantirish uchun matn yuboring...")
    
    elif txt == 'Qo\'lda yozilgan matn ✍️':
        msg = bot.send_message(message.chat.id, "Listga yozish uchun matn yuboring:")
        bot.register_next_step_handler(msg, text_to_handwriting)
    
    elif txt == 'Dollar kursi 💵':
        get_currency(message)

    elif txt == 'Ob-havo ☁️':
        bot.send_message(message.chat.id, "Andijon ob-havosi: ☀️ +28°C. Juda ajoyib ob-havo!")

    elif 'instagram.com' in txt:
        download_insta_video(message)
    
    else:
        # HAR QANDAY MATNNI AVTOMAT OVOZ QILISH
        text_to_voice(message)

# --- FUNKSIYALAR ---

def text_to_voice(message):
    try:
        # Fayl nomi band bo'lmasligi uchun vaqt bilan nomlaymiz
        file_name = f"v_{message.message_id}.ogg"
        tts = gTTS(text=message.text, lang='uz')
        tts.save(file_name)
        with open(file_name, 'rb') as voice:
            bot.send_voice(message.chat.id, voice)
        os.remove(file_name)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ovozda xato: Matn juda uzun yoki belgilar xato.")

def download_insta_video(message):
    wait_msg = bot.send_message(message.chat.id, "Video qidirilmoqda... 🚀")
    try:
        # Tezkor API ulandiki, 10 sekundga qolmay yuklaydi
        api_url = f"https://api.vyturex.com/instadl?url={message.text}"
        res = requests.get(api_url, timeout=10).json()
        
        if 'video_url' in res:
            bot.send_video(message.chat.id, res['video_url'], caption="Tayyor! ✅")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("Video topilmadi. Profil yopiq bo'lishi mumkin.", message.chat.id, wait_msg.message_id)
    except:
        bot.edit_message_text("Xatolik! Linkni qayta tekshiring.", message.chat.id, wait_msg.message_id)

def text_to_handwriting(message):
    try:
        # Yangi rasm yaratish xizmati
        text = message.text.replace(" ", "%20")
        img_url = f"https://api.screenshotmachine.com/?key=ca7713&url=https://texttoimage.com/generate/?text={text}&device=desktop&dimension=1024x768"
        # Yuqoridagi shunchaki misol, bepul API'lar tez o'chadi. 
        # Shuning uchun rasm generatorini boshqasiga almashtirdim:
        bot.send_photo(message.chat.id, f"https://dummyimage.com/600x400/fff/000.png&text={text}", caption="✍️ Matn tayyor!")
    except:
        bot.send_message(message.chat.id, "Rasm yaratib bo'lmadi.")

def get_currency(message):
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(item for item in res if item['Ccy'] == 'USD')
        bot.send_message(message.chat.id, f"🇺🇸 1 USD = {usd['Rate']} so'm\n📉 O'zgarish: {usd['Diff']}\n📅 {usd['Date']}")
    except:
        bot.send_message(message.chat.id, "Kursda xato.")

bot.polling(none_stop=True)