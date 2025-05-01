from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keep_alive import keep_alive
import asyncio
from datetime import datetime, timedelta
import pytz

TOKEN = "7700309780:AAFVb4k6AwrWKQMidbtjoRNrEsu3vOcb06c"
CHANNEL_ID = -1002333575329

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

class SessionStates(StatesGroup):
    waiting_for_count = State()

is_running = False
current_sessions = 0

@dp.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    global is_running
    if is_running:
        await message.answer("⚠️ الجلسات تعمل بالفعل!")
        return
    await message.answer("كم عدد الجلسات التي تريد تشغيلها؟ (من 1 إلى 8)")
    await state.set_state(SessionStates.waiting_for_count)

@dp.message(SessionStates.waiting_for_count)
async def get_session_count(message: Message, state: FSMContext):
    global is_running, current_sessions
    try:
        count = int(message.text)
        if count < 1 or count > 8:
            await message.answer("⚠️ أقصى عدد للجلسات هو 8.")
            return
        current_sessions = count
        is_running = True
        await message.answer("✅ بدأ إرسال الجلسات...")
        await state.clear()
        await send_sessions()
    except ValueError:
        await message.answer("⚠️ الرجاء إدخال رقم صحيح من 1 إلى 8.")

@dp.message(F.text == "/stop")
async def stop_command(message: Message):
    global is_running
    if is_running:
        is_running = False
        await message.answer("⛔️ تم إيقاف إرسال الجلسات.")
    else:
        await message.answer("لا توجد جلسات حاليًا لإيقافها.")

async def send_sessions():
    global is_running, current_sessions

    if not is_running:
        return

    alg_time = datetime.now(pytz.timezone("Africa/Algiers"))

    await bot.send_message(CHANNEL_ID,
        f"🫶  بسم الله نبدا على بركة الله\n\n"
        f"📅 • الجلسة الأولى 📚 :\n\n"
        f"🕥   • من {alg_time.strftime('%H:%M')} إلى {(alg_time + timedelta(hours=1)).strftime('%H:%M')}\n\n"
        f"بالتوفيق والسداد للجميع 💜")
    await asyncio.sleep(3600)

    if not is_running:
        return
    await bot.send_message(CHANNEL_ID,
        "🪫 راحة لمدة 10 دقائق ⌛️\n\nالأفضل أن تقضيها بعيدا عن هاتفك 💜")
    await asyncio.sleep(600)

    for i in range(2, current_sessions + 1):
        if not is_running:
            return
        start_time = alg_time + timedelta(hours=(i - 1), minutes=10)
        end_time = start_time + timedelta(hours=1)

        await bot.send_message(CHANNEL_ID,
            f"📅 • الجلسة {i} 📚 :\n\n"
            f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
            f"بالتوفيق والسداد للجميع 💜")
        await asyncio.sleep(3600)

        if i != current_sessions:
            if not is_running:
                return
            await bot.send_message(CHANNEL_ID,
                "🪫 راحة لمدة 10 دقائق ⌛️\n\nالأفضل أن تقضيها بعيدا عن هاتفك 💜")
            await asyncio.sleep(600)

    if is_running:
        await bot.send_message(CHANNEL_ID,
            "🔋 انتهت الجلسات\n\nشكرا لكم على بقاءكم معي حتى الآن ربي ينجحنا و يقدرنا كاملين و لي مقراش معنا الآن يقرا معنا المرة القادمة 💜")
        is_running = False

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
