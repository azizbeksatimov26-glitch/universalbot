import telebot
import sqlite3
import requests
import datetime
import time
import random
import psutil
import platform
from telebot import types

# ==============================================================================
# 🛡️ 1. ASOSIY KONFIGURATSIYA VA TOKEN
# ==============================================================================
API_TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(API_TOKEN)
START_TIME = time.time()

# ==============================================================================
# 📂 2. SQL DATABASE ENGINE (HAR BIR QADAMDA SELECT & UPDATE)
# ==============================================================================
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("titan_mega_hub.db", check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Foydalanuvchilar jadvali
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, 
            username TEXT, 
            full_name TEXT,
            requests_count INTEGER DEFAULT 0,
            last_activity TEXT,
            balance INTEGER DEFAULT 1000)''')
        self.conn.commit()

    def sync_user_data(self, user_id, username, full_name):
        cursor = self.conn.cursor()
        
        # 1. SELECT: Foydalanuvchini bazadan qidirish
        cursor.execute("SELECT requests_count FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if result is None:
            # Yangi foydalanuvchini qo'shish
            cursor.execute("INSERT INTO users (user_id, username, full_name, last_activity) VALUES (?, ?, ?, ?)",
                           (user_id, username, full_name, now))
        else:
            # 2. UPDATE: Ma'lumotlarni yangilash va hisoblagichni oshirish
            new_count = result[0] + 1
            cursor.execute("UPDATE users SET requests_count = ?, last_activity = ?, username = ? WHERE user_id = ?",
                           (new_count, now, username, user_id))
        
        self.conn.commit()

db = DatabaseManager()

# ==============================================================================
# 📚 3. DATA VAULT: ISMLAR, IT DARSLIKLAR VA MA'LUMOTLAR
# ==============================================================================
class DataVault:
    # Ismlar (M, K, X qoidalari asosida)
    ISMLAR = {
        "Nurbekjon": {
            "m": "Nurli, omadli va beklar avlodiga mansub mard yigit.",
            "k": "Arabcha (Nur) va O'zbekcha (Bek) so'zlaridan tashkil topgan.",
            "x": "Krasafchik, qizlarni ajali va IT olamining bo'lajak qiroli."
        },
        "Sardor": {
            "m": "Guruh sardori, yo'lboshchi va mas'uliyatli rahbar.",
            "k": "Fors-tojik tilidan olingan bo'lib, 'boshliq' demakdir.",
            "x": "Qat'iyatli, so'zida turadigan va do'stlariga sodiq."
        }
        # BU YERGA 1000 TA ISM QO'SHILSA KOD 1500 QATORGA YETADI
    }

    # IT Darsliklar (O'quv moduli)
    IT_MODULES = {
        "Python": "🐍 Python - bu sun'iy intellekt va backend uchun eng zo'r til.",
        "Django": "🌐 Django - Python asosidagi eng xavfsiz web framework.",
        "JavaScript": "📜 JavaScript - web saytlarga jon beruvchi til.",
        "SQL": "🗄 SQL - ma'lumotlar bazasi bilan ishlash tili."
    }

# ==============================================================================
# 🎮 4. KEYBOARD FACTORY (13 TA TUGMA)
# ==============================================================================
class Keyboards:
    @staticmethod
    def main_menu():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        # 13 ta tugma joylashuvi
        buttons = [
            "🔍 Ism Ma'nosi", "✨ Shriftlar", "💻 IT Darslar",
            "🌤 Ob-havo", "💹 Valyuta", "🎮 O'yinlar",
            "🖼 Rasmlar", "📜 Hikmatlar", "👤 Profil",
            "📊 Statistika", "⏳ Taymer", "⚙️ Sozlamalar",
            "🆘 Yordam"
        ]
        markup.add(*(types.KeyboardButton(b) for b in buttons))
        return markup

    @staticmethod
    def back_btn():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("⬅️ Orqaga"))
        return markup

# ==============================================================================
# 🤖 5. ASOSIY BOT HANDLERLARI
# ==============================================================================

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid, uname, fname = message.chat.id, message.from_user.username, message.from_user.first_name
    db.sync_user_data(uid, uname, fname) # SQL amalga oshirildi
    
    welcome_text = (
        f"👋 **Salom, {fname}!**\n\n"
        f"Men **TITAN MEGA HUB** botiman. Siz uchun 13 xil funksiyani tayyorlab qo'ydim.\n"
        f"Siz hozir Andijon hududidagi eng kuchli botlardan biridasiz!"
    )
    bot.send_message(uid, welcome_text, reply_markup=Keyboards.main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def central_router(message):
    uid = message.chat.id
    text = message.text
    db.sync_user_data(uid, message.from_user.username, message.from_user.first_name)

    if text == "🔍 Ism Ma'nosi":
        msg = bot.send_message(uid, "✍️ Ismni yuboring:", reply_markup=Keyboards.back_btn())
        bot.register_next_step_handler(msg, name_logic)

    elif text == "✨ Shriftlar":
        msg = bot.send_message(uid, "✍️ Matn yuboring:", reply_markup=Keyboards.back_btn())
        bot.register_next_step_handler(msg, font_logic)

    elif text == "💻 IT Darslar":
        res = "📚 **IT Kurslari Ro'yxati:**\n\n"
        for key, val in DataVault.IT_MODULES.items():
            res += f"🔹 **{key}**: {val}\n"
        bot.send_message(uid, res, parse_mode="Markdown")

    elif text == "💹 Valyuta":
        try:
            data = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
            usd = data[0]['Rate']
            eur = data[1]['Rate']
            bot.send_message(uid, f"🇺🇸 1 USD = {usd} so'm\n🇪🇺 1 EUR = {eur} so'm")
        except:
            bot.send_message(uid, "⚠️ Valyuta kursini olib bo'lmadi.")

    elif text == "📊 Statistika":
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))
        bot.send_message(uid, f"🚀 **Tizim Holati:**\n\n🔥 CPU: {cpu}%\n📟 RAM: {ram}%\n⏳ Uptime: {uptime}")

    elif text == "🎮 O'yinlar":
        bot.send_dice(uid, '🎰')
        bot.send_message(uid, "🎰 O'yin ishga tushdi! Omadingizni sinang.")

    elif text == "👤 Profil":
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
        user = cursor.fetchone()
        profile = (
            f"👤 **Sizning Profilingiz:**\n\n"
            f"🆔 ID: `{user[0]}`\n"
            f"👤 Ism: {user[2]}\n"
            f"📈 Buyruqlar: {user[3]} ta\n"
            f"💰 Balans: {user[5]} ball"
        )
        bot.send_message(uid, profile, parse_mode="Markdown")

    elif text == "⬅️ Orqaga":
        bot.send_message(uid, "Asosiy menyuga qaytdingiz.", reply_markup=Keyboards.main_menu())

# ==============================================================================
# 🛠 6. LOGIKA FUNKSIYALARI
# ==============================================================================

def name_logic(message):
    if message.text == "⬅️ Orqaga":
        bot.send_message(message.chat.id, "Menyu:", reply_markup=Keyboards.main_menu())
        return
    name = message.text.capitalize()
    data = DataVault.ISMLAR.get(name)
    if data:
        res = f"💎 **Ism:** {name}\n📜 **Ma'nosi:** {data['m']}\n🌍 **Kelib chiqishi:** {data['k']}\n🧠 **Xususiyati:** {data['x']}"
        bot.send_message(message.chat.id, res, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Topilmadi. (Bazani kengaytirish kerak)")

def font_logic(message):
    if message.text == "⬅️ Orqaga":
        bot.send_message(message.chat.id, "Menyu:", reply_markup=Keyboards.main_menu())
        return
    t = message.text
    res = f"1. 𝕹𝖚𝖗𝖇𝖊𝖐𝖏𝖔𝖓: {t}\n2. 𝓝𝓾𝓻𝓫𝓮𝓴𝓳𝓸𝓷: {t}\n3. 𝙉𝙪𝙧𝙗𝙚𝙠joint: {t}\n4. ℕ𝕦𝕣𝕓𝕖𝕜𝕛𝕠𝕟: {t}"
    bot.send_message(message.chat.id, res)

# ==============================================================================
# 🚀 7. RUN BOT
# ==============================================================================
if __name__ == "__main__":
    print("TITAN MEGA HUB ishga tushdi...")
    bot.infinity_polling()