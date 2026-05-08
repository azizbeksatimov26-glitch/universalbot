import telebot
from telebot import types
import random

# BOT TOKEN
TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)

# Tinchlantiruvchi gaplar va motivatsiya
tinchlan_gaplar = [
    "Nurbekjon, asabiylashmang polvon! Hamma narsa o'tib ketadi, kod esa qoladi. 💪",
    "IT-da xato bo'lishi — bu tajriba degani. Siz hali Andijonning eng zo'r Seniori bo'lasiz! 🚀",
    "Krasafchik, bitta choy ichib oling, asablar joyiga tushadi. Botlar hali sizga xizmat qiladi! 🍵",
    "Real Madrid ham yutqazib turadi, lekin oxiri baribir chempion bo'ladi! Siz ham shunday! ⚽️",
    "Bitta xato tufayli to'xtab qolmaymiz. Sizda hali katta loyihalar oldinda! 🔥",
    "Dasturlash — bu sabr sporti. Sizda esa sabr bor, Nurbekjon krasafchik!",
    "Hamma 'haromi' xatolarni birga yengamiz. Hozircha dam oling. 😎"
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Meni tinchlantir 🧘‍♂️', 'Motivatsiya ber 🔥')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        f"Salom, Nurbekjon krasafchik qizlarni ajali! 👋\nBu bot faqat sizning asabingizni asrash uchun yaratildi. Hech qanday xatosiz ishlaydi!", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if message.text == 'Meni tinchlantir 🧘‍♂️' or message.text == 'Motivatsiya ber 🔥':
        # Tasodifiy gap tanlash
        gap = random.choice(tinchlan_gaplar)
        bot.send_message(message.chat.id, gap)
    else:
        bot.send_message(message.chat.id, "Nurbekjon, pastdagi tugmalarni bosing, asabni asraymiz! 😊", reply_markup=main_menu())

bot.infinity_polling()