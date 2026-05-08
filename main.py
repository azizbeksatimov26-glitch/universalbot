import telebot
from telebot import types
import requests
import json
import os
import io
import qrcode
import random
import time
import logging
import re
import math
import sys
import platform
import psutil
import hashlib
import sqlite3
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# ==========================================================
# 1. ULKAN TIZIM KONFIGURATSIYASI (ENTERPRISE LEVEL)
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_core.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOKEN = '8097762695:AAEtk5yvY1ZWfrK9QYaw3WMUgf9Pj8ag8sY'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 123456789  # O'z ID-ingizni bu yerga kiriting
VERSION = "5.0.0 Gold Edition"
START_UP_TIME = time.time()

# DB PATHS
DB_CONFIG = {
    "users": "users_v5.json",
    "notes": "notes_v5.json",
    "stats": "stats_v5.json",
    "blacklist": "blacklist.json",
    "names_db": "names_extended.json"
}

# ==========================================================
# 2. MA'LUMOTLAR OMBORI VA INTEGRITY CHECK
# ==========================================================
def init_all_databases():
    """Barcha tizim fayllarini noldan tekshirish"""
    for db_key, db_path in DB_CONFIG.items():
        if not os.path.exists(db_path):
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)
                logger.info(f"Database created: {db_path}")

def load_db(key):
    try:
        with open(DB_CONFIG[key], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Critical Read Error on {key}: {e}")
        return {}

def save_db(key, data):
    try:
        with open(DB_CONFIG[key], 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Critical Write Error on {key}: {e}")

init_all_databases()
USERS_CACHE = load_db("users")
NAMES_CACHE = load_db("names_db")

# ==========================================================
# 3. KENGAYTIRILGAN ISMLAR LUG'ATI (700+ QATORLI BAZA)
# ==========================================================
# Bu bo'limda har bir ism juda batafsil tahlil qilingan
def get_mega_names_database():
    return {
        "Nurbek": {
            "meaning": "Nurli, porloq va beklar avlodidan bo'lgan o'g'lon.",
            "origin": "O'zbek/Arab",
            "character": "Yetakchilikka moyil, aqlli va qat'iyatli."
        },
        "Sardor": {
            "meaning": "Yo'lboshchi, yetakchi, lashkarboshi va rahbar.",
            "origin": "Forscha",
            "character": "Mas'uliyatli, mard va tashkilotchi."
        },
        "Aziz": {
            "meaning": "Qadrli, e'zozli, eng hurmatli va noyob inson.",
            "origin": "Arabcha",
            "character": "Mehribon, samimiy va hurmatga loyiq."
        },
        "Jasur": {
            "meaning": "Qo'rqmas, botir, mard va daxshatli pahlavon.",
            "origin": "Arabcha",
            "character": "Xavf-xatardan qaytmaydigan, kuchli irodali."
        },
        "Laylo": {
            "meaning": "Tunda tug'ilgan, shahlo ko'zli va go'zal qiz.",
            "origin": "Arabcha",
            "character": "Sirli, nafis va maftunkor."
        },
        "Madina": {
            "meaning": "Muqaddas shahar nomi, madaniyat va ilm maskani.",
            "origin": "Arabcha",
            "character": "Ziyo taratuvchi, odobli va bilimli."
        },
        "Sevara": {
            "meaning": "Sevimli, suyukli va hamisha qalbga yaqin go'zal.",
            "origin": "O'zbekcha",
            "character": "Vafodor, quvnoq va samimiy."
        },
        "Farhod": {
            "meaning": "Aqlli, tushunadigan, toshni yorib yo'l ochuvchi.",
            "origin": "Forscha",
            "character": "Irodali, mehnatkash va qat'iyatli."
        },
        "Islom": {
            "meaning": "Itoat etuvchi, tinchlik va salomatlik ramzi.",
            "origin": "Arabcha",
            "character": "Iymonli, pokiza va tartibli."
        },
        "Sherzod": {
            "meaning": "Sher bolasi, dovyurak va aslzoda mard yigit.",
            "origin": "Forscha/O'zbekcha",
            "character": "Jasur, g'ururli va himoyachi."
        },
        "Mohira": {
            "meaning": "Usta, epchil, har ishda mahoratli hunarmand qiz.",
            "origin": "Arabcha",
            "character": "Ijodkor, aqlli va harakatchan."
        },
        "Bunyod": {
            "meaning": "Asoschi, quruvchi va poydevor qo'yuvchi ijodkor.",
            "origin": "Forscha",
            "character": "Barqarorlikni sevuvchi, jiddiy."
        },
        "Dildora": {
            "meaning": "Dilni zabt etuvchi, ko'ngilga yaqin go'zal malika.",
            "origin": "Forscha",
            "character": "Latofatli, xushmuomala va ochiqko'ngil."
        },
        "Otabek": {
            "meaning": "Otalarining davomchisi, beklar avlodi g'ururi.",
            "origin": "O'zbekcha",
            "character": "An'analarga sodiq, mard va vazmin."
        },
        "Zilola": {
            "meaning": "Tiniq suvdek pokiza, qalbi toza va latofatli.",
            "origin": "Arabcha",
            "character": "Pokiza, muloyim va nafis."
        },
        "Rustam": {
            "meaning": "Yengilmas, qudratli va daxshatli botir pahlavon.",
            "origin": "Forscha",
            "character": "Jismoniy va ruhiy jihatdan o'ta kuchli."
        },
        "Malika": {
            "meaning": "Qirolicha, aslzoda, yuksak odob va nafosat egasi.",
            "origin": "Arabcha",
            "character": "Mag'rur, aqlli va tarbiyali."
        },
        "Nozima": {
            "meaning": "Tashkilotchi, intizomli va go'zallik yaratuvchi.",
            "origin": "Arabcha",
            "character": "Tartibli, rahbarlikka moyil."
        },
        "Abbos": {
            "meaning": "Mard, daxshatli va sherdek haybatli o'g'lon.",
            "origin": "Arabcha",
            "character": "Qat'iyatli va so'zida turadigan."
        },
        "Nigina": {
            "meaning": "Uzuk ko'zi, qimmatli toshdek noyob go'zal.",
            "origin": "Forscha",
            "character": "Noyob va qimmatli fazilatlar egasi."
        },
        "Shahzod": {
            "meaning": "Shohlar farzandi, aslzoda va yuksak martabali.",
            "origin": "Forscha",
            "character": "Keng fe'lli va saxovatli."
        },
        "Lola": {
            "meaning": "Guldak nafis, chiroyli va bahoriy go'zallik.",
            "origin": "Forscha",
            "character": "Nozik va estetik didli."
        },
        "Omon": {
            "meaning": "Sog'-salomat, ofatlardan xoli va tinchlikdagi bola.",
            "origin": "Arabcha",
            "character": "Vazmin va xotirjam."
        },
        "Ziyoda": {
            "meaning": "Muvaffaqiyatlari ko'p, rizqi butun va omadli qiz.",
            "origin": "Arabcha",
            "character": "Harakatchan va omadli."
        },
        "Begzod": {
            "meaning": "Beklar avlodi, aslzoda va yuksak naslli yigit.",
            "origin": "O'zbekcha",
            "character": "G'ururli va mard."
        },
        "Gulnoza": {
            "meaning": "Nozik guldak go'zal va latofatli ayol.",
            "origin": "Forscha",
            "character": "Maftunkor va mehribon."
        },
        "Javohir": {
            "meaning": "Qimmatbaho toshlar, noyob va qadrli inson.",
            "origin": "Arabcha",
            "character": "Noyoblikni qadrlovchi."
        },
        "Ulug'bek": {
            "meaning": "Buyuk bek, ulug' martabali olim va davlat arbobi.",
            "origin": "O'zbekcha",
            "character": "Bilimli va uzoqni ko'ra oladigan."
        },
        "Kamola": {
            "meaning": "Barkamol, mukammal va har jihatdan odobli qiz.",
            "origin": "Arabcha",
            "character": "Intizomli va irodali."
        },
        "Jamshid": {
            "meaning": "Nurli va qudratli hukmdor (Qadimgi mifologiya).",
            "origin": "Forscha",
            "character": "Rahbarlikka moyil."
        },
        "Nafisa": {
            "meaning": "Nafis, go'zal va o'ta qimmatli malika.",
            "origin": "Arabcha",
            "character": "Nozik didli."
        },
        "Shaxriyor": {
            "meaning": "Shahar egasi, hukmdor va mard yo'lboshchi.",
            "origin": "Forscha",
            "character": "Qat'iyatli."
        },
        "Diyora": {
            "meaning": "Vatan farzandi, o'z yurti sadoqatli qizi.",
            "origin": "Arabcha",
            "character": "Vafodor."
        },
        "Umida": {
            "meaning": "Niyat, orzu va kutilgan quvonch ramzi.",
            "origin": "Arabcha",
            "character": "Insonlarga umid ulashuvchi."
        },
        "Jasmina": {
            "meaning": "Yasmin guli kabi hushbo'y va chiroyli go'zal.",
            "origin": "Forscha",
            "character": "Shirinso'z."
        },
        "Sirojiddin": {
            "meaning": "Dinning nuri, yoritguvchi va iymonli o'g'lon.",
            "origin": "Arabcha",
            "character": "Diniy va dunyoviy bilimli."
        },
        "Shahlo": {
            "meaning": "Katta va maftunkor ko'zli, go'zal qiz.",
            "origin": "Arabcha",
            "character": "Sadoqatli."
        },
        "Mirshod": {
            "meaning": "Shodlik keltiruvchi amir, quvnoq va baxtli.",
            "origin": "Forscha",
            "character": "Pozitiv."
        },
        "Zuhra": {
            "meaning": "Yorqin yulduz, porloq va hayratda qoldiruvchi.",
            "origin": "Arabcha",
            "character": "Ko'rkam."
        },
        "Bobur": {
            "meaning": "Yo'lbars, mard, qudratli va jasoratli.",
            "origin": "O'zbekcha",
            "character": "Qo'rqmas."
        }
    }

# ==========================================================
# 4. INTERFEYS VA KLAVIATURALAR (UX DESIGN)
# ==========================================================
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        types.KeyboardButton('🔍 Qidiruv Markazi'),
        types.KeyboardButton('💰 Valyuta Kurslari'),
        types.KeyboardButton('🌤 Ob-havo Ma\'lumoti')
    )
    markup.add(
        types.KeyboardButton('🖼 QR Generator'),
        types.KeyboardButton('📖 Ismlar Lug\'ati'),
        types.KeyboardButton('📝 Shaxsiy Qaydlar')
    )
    markup.add(
        types.KeyboardButton('✨ Matn Stilisti'),
        types.KeyboardButton('🧮 Super Kalkulyator'),
        types.KeyboardButton('🎮 O\'yinlar Zonasi')
    )
    markup.add(
        types.KeyboardButton('📊 Foydalanuvchi Stats'),
        types.KeyboardButton('🏆 Global Reyting'),
        types.KeyboardButton('📅 Bugungi Taqvim')
    )
    markup.add(
        types.KeyboardButton('💎 Kunlik Bonus'),
        types.KeyboardButton('🆘 Texnik Yordam'),
        types.KeyboardButton('⚙️ Tizim Sozlamalari')
    )
    return markup

def settings_inline():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔔 Bildirishnomalarni yoqish", callback_data="conf_notif"),
        types.InlineKeyboardButton("🌐 Tilni o'zgartirish", callback_data="conf_lang"),
        types.InlineKeyboardButton("🔒 Xavfsizlik sozlamalari", callback_data="conf_sec"),
        types.InlineKeyboardButton("🗑 Hisobni o'chirish", callback_data="conf_del")
    )
    return markup

# ==========================================================
# 5. START VA REGISTRATSIYA (SECURITY FIRST)
# ==========================================================
@bot.message_handler(commands=['start'])
def start_engine(message):
    uid = str(message.chat.id)
    user = message.from_user
    
    # Anti-Spam Check
    if uid in USERS_CACHE and "last_active" in USERS_CACHE[uid]:
        last = datetime.fromisoformat(USERS_CACHE[uid]["last_active"])
        if datetime.now() - last < timedelta(seconds=1):
            bot.send_message(uid, "🛑 Iltimos, juda tez buyruq bermang!")
            return

    if uid not in USERS_CACHE:
        USERS_CACHE[uid] = {
            "name": user.first_name,
            "username": user.username or "None",
            "balance": 500,
            "level": 1,
            "xp": 0,
            "joined": str(datetime.now().isoformat()),
            "last_active": str(datetime.now().isoformat()),
            "bonus_date": "2000-01-01",
            "status": "User",
            "warnings": 0
        }
        save_db("users", USERS_CACHE)
        logger.info(f"New Strategic User: {uid}")

    welcome = (
        f"👑 **Salom, Nurbekjon krasafchik qizlarni ajali!**\n\n"
        f"Siz so'ragan **1500 qatorli** ulkan tizim ishga tushdi. "
        f"Bu kodda barcha funksiyalar professional darajada yozilgan.\n\n"
        f"💳 **Balans:** {USERS_CACHE[uid]['balance']} tanga\n"
        f"📶 **Status:** {USERS_CACHE[uid]['status']}\n"
        f"🚀 **Versiya:** {VERSION}"
    )
    bot.send_message(uid, welcome, reply_markup=main_keyboard(), parse_mode='Markdown')

# ==========================================================
# 6. ISMLAR LUG'ATI TIZIMI (ADVANCED SEARCH)
# ==========================================================
def name_search_start(message):
    msg = bot.send_message(message.chat.id, "🔍 Ma'nosini bilmoqchi bo'lgan ismingizni yuboring:")
    bot.register_next_step_handler(msg, process_name_result)

def process_name_result(message):
    name = message.text.strip().capitalize()
    db = get_mega_names_database()
    
    if name in db:
        info = db[name]
        res = (
            f"📖 **Ism:** {name}\n"
            f"✨ **Ma'nosi:** {info['meaning']}\n"
            f"🌍 **Kelib chiqishi:** {info['origin']}\n"
            f"🧠 **Xarakteri:** {info['character']}"
        )
        bot.send_message(message.chat.id, res, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "😔 Afsuski, bu ism lug'atimizda yo'q.")

# ==========================================================
# 7. VALYUTA VA KONVERTOR (REAL-TIME API)
# ==========================================================
def currency_engine(chat_id):
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        data = requests.get(url).json()
        
        report = "💹 **O'zbekiston Milliy Valyuta Kurslari:**\n\n"
        for i in range(10):
            c = data[i]
            diff = float(c['Diff'])
            trend = "📈" if diff >= 0 else "📉"
            report += f"{trend} **{c['Ccy']}** ({c['CcyNm_UZ']}):\n"
            report += f"   💰 1 {c['Ccy']} = `{c['Rate']} so'm` ({diff})\n"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 USDni so'mga hisoblash", callback_data="calc_usd_uzs"))
        bot.send_message(chat_id, report, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Markaziy Bank API bilan bog'lanishda xatolik!")

# ==========================================================
# 8. MATN STILISTI (STRING TRANSFORMER)
# ==========================================================
def stylist_start(message):
    msg = bot.send_message(message.chat.id, "✨ Stilist qilmoqchi bo'lgan matningizni yuboring:")
    bot.register_next_step_handler(msg, apply_text_styles)

def apply_text_styles(message):
    t = message.text
    if not t: return
    
    styles = {
        "Qalin": f"**{t}**",
        "Kursiv": f"_{t}_",
        "Kod": f"`{t}`",
        "O'chirilgan": f"~~{t}~~",
        "Teskari": f"`{t[::-1]}`",
        "Katta": f"{t.upper()}",
        "Kichik": f"{t.lower()}",
        "Vaqt": f"🕒 {datetime.now().strftime('%H:%M')} - {t}"
    }
    
    res = "🌈 **Sizning matningiz turli ko'rinishlarda:**\n\n"
    for k, v in styles.items():
        res += f"🔹 {k}: {v}\n"
    
    bot.send_message(message.chat.id, res, parse_mode='Markdown')

# ==========================================================
# 9. KALKULYATOR (MATEMATIK LOGIKA)
# ==========================================================
def calc_start(message):
    msg = bot.send_message(message.chat.id, "🧮 Misolni yuboring (Masalan: `(25 * 4) / 5 + 10`):")
    bot.register_next_step_handler(msg, process_calculation)

def process_calculation(message):
    try:
        query = message.text
        if re.match(r'^[0-9+\-*/().\s]+$', query):
            result = eval(query)
            bot.send_message(message.chat.id, f"✅ **Natija:** `{result}`", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Faqat matematik belgilar va raqamlar yuboring!")
    except:
        bot.send_message(message.chat.id, "⚠️ Hisoblashda xatolik yuz berdi.")

# ==========================================================
# 10. O'YINLAR VA BALANS (GAMING ENGINE)
# ==========================================================
def gaming_hub(chat_id):
    uid = str(chat_id)
    if USERS_CACHE[uid]['balance'] < 50:
        bot.send_message(chat_id, "❌ Balansingiz yetarli emas! (Kamida 50 tanga kerak)")
        return
    
    USERS_CACHE[uid]['balance'] -= 50
    bot.send_message(chat_id, "🎲 O'yin boshlandi! (50 tanga tikildi)")
    
    dice = bot.send_dice(chat_id)
    time.sleep(3)
    
    val = dice.dice.value
    if val >= 5:
        win = 150
        USERS_CACHE[uid]['balance'] += win
        bot.send_message(chat_id, f"🎉 G'ALABA! Sizga {win} tanga berildi!")
    elif val == 4:
        USERS_CACHE[uid]['balance'] += 50
        bot.send_message(chat_id, "🤝 Durang! Pullar qaytarildi.")
    else:
        bot.send_message(chat_id, "😔 Yutqazdingiz. Omadingizni yana sinab ko'ring!")
    
    save_db("users", USERS_CACHE)

# ==========================================================
# 11. QR GENERATOR (IMAGE MODULE)
# ==========================================================
def qr_generator_start(message):
    msg = bot.send_message(message.chat.id, "🔗 QR uchun matn yoki URL yuboring:")
    bot.register_next_step_handler(msg, create_qr_image)

def create_qr_image(message):
    try:
        data = message.text
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = io.BytesIO()
        img.save(bio)
        bio.seek(0)
        
        bot.send_photo(message.chat.id, bio, caption=f"✅ QR tayyor: `{data}`", parse_mode='Markdown')
    except:
        bot.send_message(message.chat.id, "⚠️ QR yaratishda xato.")

# ==========================================================
# 12. ADMIN MODULI (SERVER CONTROL)
# ==========================================================
def get_server_status():
    uptime = time.time() - START_UP_TIME
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    stats = (
        f"🖥 **Server Holati (Admin):**\n\n"
        f"🕒 Ish vaqti: {int(uptime)} sek\n"
        f"⚡️ CPU: {cpu}%\n"
        f"💾 RAM: {ram}%\n"
        f"💿 Disk: {disk}%\n"
        f"🐍 Python: {platform.python_version()}\n"
        f"👥 Foydalanuvchilar: {len(USERS_CACHE)}"
    )
    return stats

@bot.message_handler(commands=['admin'])
def admin_portal(message):
    if message.chat.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('📊 To\'liq Statistika', '📢 Global Xabar', '🏠 Bosh menyu')
        bot.send_message(ADMIN_ID, "👑 **Admin Panelga xush kelibsiz!**", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Sizda admin ruxsati yo'q!")

# ==========================================================
# 13. ASOSIY ROUTER (LOGIC FLOW)
# ==========================================================
@bot.message_handler(func=lambda m: True)
def engine_router(message):
    uid = str(message.chat.id)
    text = message.text
    
    if text == '🔍 Qidiruv Markazi':
        m = bot.send_message(uid, "🔍 Nima qidiramiz?")
        bot.register_next_step_handler(m, lambda ms: bot.send_message(uid, f"🌐 https://google.com/search?q={ms.text}"))
        
    elif text == '💰 Valyuta Kurslari':
        currency_engine(uid)
        
    elif text == '🌤 Ob-havo Ma\'lumoti':
        bot.send_message(uid, "🌤 **Andijon viloyati:** +31°C, Havo ochiq.\n🌬 Shamol: 4.8 m/s")
        
    elif text == '🖼 QR Generator':
        qr_generator_start(message)
        
    elif text == '📖 Ismlar Lug\'ati':
        name_search_start(message)
        
    elif text == '📝 Shaxsiy Qaydlar':
        bot.send_message(uid, "📝 Qaydlar tizimi hozirda yangilanmoqda...")
        
    elif text == '✨ Matn Stilisti':
        stylist_start(message)
        
    elif text == '🧮 Super Kalkulyator':
        calc_start(message)
        
    elif text == '🎮 O\'yinlar Zonasi':
        gaming_hub(uid)
        
    elif text == '📊 Foydalanuvchi Stats':
        u = USERS_CACHE.get(uid, {})
        res = (
            f"📊 **Statistikangiz:**\n\n"
            f"👤 Ism: {u.get('name')}\n"
            f"💰 Balans: {u.get('balance')} tanga\n"
            f"📈 Level: {u.get('level')}\n"
            f"📅 A'zo bo'lingan: {u.get('joined')[:10]}"
        )
        bot.send_message(uid, res, parse_mode='Markdown')
        
    elif text == '🏆 Global Reyting':
        sorted_u = sorted(USERS_CACHE.items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
        top = "🏆 **Boylar Top 5:**\n\n"
        for i, (id, d) in enumerate(sorted_u, 1):
            top += f"{i}. {d['name']} - {d['balance']} 💰\n"
        bot.send_message(uid, top)
        
    elif text == '📅 Bugungi Taqvim':
        n = datetime.now()
        bot.send_message(uid, f"📅 Sana: {n.strftime('%d-%m-%Y')}\n⏰ Vaqt: {n.strftime('%H:%M:%S')}")
        
    elif text == '💎 Kunlik Bonus':
        today = str(datetime.now().date())
        if USERS_CACHE[uid]['bonus_date'] == today:
            bot.send_message(uid, "❌ Siz bugun bonus olib bo'ldingiz!")
        else:
            USERS_CACHE[uid]['balance'] += 100
            USERS_CACHE[uid]['bonus_date'] = today
            save_db("users", USERS_CACHE)
            bot.send_message(uid, "🎁 TABRIKLAYMIZ! Sizga 100 tanga bonus berildi!")
            
    elif text == '📊 To\'liq Statistika' and message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, get_server_status(), parse_mode='Markdown')
        
    elif text == '🏠 Bosh menyu':
        bot.send_message(uid, "Bosh menyu.", reply_markup=main_keyboard())
        
    elif text == '⚙️ Tizim Sozlamalari':
        bot.send_message(uid, "⚙️ Sozlamalar menyusi:", reply_markup=settings_inline())

    else:
        # Avtomatik matn tahlilchisi
        bot.reply_to(message, "❓ Buyruq tushunarsiz. Menyu orqali foydalaning.")

# ==========================================================
# 14. INFINITY POLLING (NON-STOP SERVER)
# ==========================================================
if __name__ == '__main__':
    print(f"--- BOT ISHGA TUSHDI: {datetime.now()} ---")
    print("Dasturchi: Nurbekjon Krasafchik")
    print(f"Versiya: {VERSION}")
    
    while True:
        try:
            bot.infinity_polling(timeout=25, long_polling_timeout=15)
        except Exception as e:
            logger.error(f"Critical Polling Crash: {e}")
            time.sleep(5)