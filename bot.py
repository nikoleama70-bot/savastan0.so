import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiohttp import web

# एनवायरनमेंट वेरिएबल्स से टोकन और एडमिन आईडी उठाना
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8631580614"))
PORT = int(os.getenv("PORT", 10000))  # Render के लिए पोर्ट

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user = message.from_user
    # यूजर को रिप्लाई भेजना
    await message.reply("नमस्ते! आपका सावस्तान0 बोट सफलता से लाइव है।")
    
    # अगर यूजर एडमिन नहीं है, तो एडमिन को चुपचाप नोटिफिकेशन भेजना
    if user.id != ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID, 
                f"🔔 **नया यूजर एक्टिविटी:**\n\nID: `{user.id}`\nनाम: {user.full_name}\nयूजरनेम: @{user.username}"
            )
        except Exception as e:
            print(e)

# Render के पोर्ट टाइमआउट से बचने के लिए नकली वेब सर्वर
async def handle(request):
    return web.Response(text="Bot is running and alive!")

app = web.Application()
app.router.add_get('/', handle)

async def on_startup(dispatcher):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    
