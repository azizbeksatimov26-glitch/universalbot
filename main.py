import telebot
from telebot import types
from gtts import gTTS
import requests
import os
import uuid
from PIL import Image, ImageDraw, ImageFont

TOKEN = 'TOKENINGIZNI_QOYING'
bot = telebot.TeleBot(TOKEN)

# ================= MENU =================

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("Insta link 🔗")
    btn2 = types.KeyboardButton("Voice message 🎤")
    btn3 = types.KeyboardButton("Qo'lda yozilgan matn ✍️")
    btn4 = types.KeyboardButton("Dollar kursi 💵")
    btn5 = types.KeyboardButton("Ob-havo ☁️")

    markup.add(btn1, btn2)
    markup.add(btn3)
    markup.add(btn4, btn5)

    return markup

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Salom {message.from_user.first_name} 👋",
        reply_markup=main_menu()
    )

# ================= STATES =================

user_mode = {}

# ================= BUTTONS =================

@bot.message_handler(func=lambda m: m.text in [
    "Voice message 🎤",
    "Qo'lda yozilgan matn ✍️",
    "Insta link 🔗",
    "Dollar kursi 💵",
    "Ob-havo ☁️"
])
def buttons(message):

    txt = message.text

    if txt == "Voice message 🎤":
        user_mode[message.chat.id] = "voice"
        bot.send_message(message.chat.id, "Matn yuboring 🎤")

    elif txt == "Qo'lda yozilgan matn ✍️":
        user_mode[message.chat.id] = "hand"
        bot.send_message(message.chat.id, "Matn yuboring ✍️")

    elif txt == "Insta link 🔗":
        user_mode[message.chat.id] = "insta"
        bot.send_message(message.chat.id, "Instagram link yuboring 🔗")

    elif txt == "Dollar kursi 💵":
        get_dollar(message)

    elif txt == "Ob-havo ☁️":
        get_weather(message)

# ================= MAIN =================

@bot.message_handler(func=lambda m: True)
def all_messages(message):

    mode = user_mode.get(message.chat.id)

    if mode == "voice":
        text_to_voice(message)

    elif mode == "hand":
        handwritten_text(message)

    elif mode == "insta":
        instagram_download(message)

# ================= VOICE =================

def text_to_voice(message):

    filename = f"{uuid.uuid4().hex}.mp3"

    try:
        tts = gTTS(text=message.text, lang='uz')
        tts.save(filename)

        with open(filename, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)

    except:
        bot.send_message(message.chat.id, "Xatolik yuz berdi.")

    finally:
        if os.path.exists(filename):
            os.remove(filename)

# ================= HANDWRITING =================

def handwritten_text(message):

    text = message.text

    img = Image.new('RGB', (1000, 500), color='white')

    draw = ImageDraw.Draw(img)

    # Font yuklab qo'yishingiz kerak:
    # handwriting.ttf

    font = ImageFont.truetype("handwriting.ttf", 42)

    draw.text((80, 120), text, fill='black', font=font)

    filename = f"{uuid.uuid4().hex}.png"

    img.save(filename)

    with open(filename, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

    os.remove(filename)

# ================= INSTAGRAM =================

def instagram_download(message):

    try:

        wait = bot.send_message(message.chat.id, "Yuklanmoqda ⏳")

        url = f"https://api.vyturex.com/instadl?url={message.text}"

        response = requests.get(url).json()

        if "video_url" in response:

            bot.send_video(
                message.chat.id,
                response["video_url"],
                caption="Mana video ✅"
            )

        else:
            bot.send_message(message.chat.id, "Video topilmadi ❌")

        bot.delete_message(message.chat.id, wait.message_id)

    except:
        bot.send_message(message.chat.id, "Instagram API xatolik berdi.")

# ================= DOLLAR =================

def get_dollar(message):

    try:

        data = requests.get(
            "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        ).json()

        usd = next(x for x in data if x["Ccy"] == "USD")

        bot.send_message(
            message.chat.id,
            f"""
🇺🇸 Dollar kursi

1 USD = {usd['Rate']} so'm

📅 Sana: {usd['Date']}
"""
        )

    except:
        bot.send_message(message.chat.id, "Xatolik.")

# ================= WEATHER =================

def get_weather(message):

    try:

        api = "https://api.openweathermap.org/data/2.5/weather?q=Andijan&appid=API_KEY&units=metric"

        data = requests.get(api).json()

        temp = data["main"]["temp"]

        desc = data["weather"][0]["description"]

        bot.send_message(
            message.chat.id,
            f"""
🌤 Andijon ob-havosi

🌡 Harorat: {temp}°C
☁️ Holat: {desc}
"""
        )

    except:
        bot.send_message(message.chat.id, "Ob-havo olinmadi.")

# ================= RUN =================

print("Bot ishladi...")

bot.infinity_polling()