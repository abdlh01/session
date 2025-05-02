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
is_test_mode = False

@dp.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    global is_running, is_test_mode
    if is_running:
        await message.answer("⚠️ الجلسات تعمل بالفعل!")
        return
    is_test_mode = False
    await message.answer("كم عدد الجلسات التي تريد تشغيلها؟ (من 1 إلى 8)")
    await state.set_state(SessionStates.waiting_for_count)

@dp.message(F.text == "/test")
async def test_command(message: Message, state: FSMContext):
    global is_running, is_test_mode
    if is_running:
        await message.answer("⚠️ الجلسات تعمل بالفعل!")
        return
    is_test_mode = True
    await message.answer("🔎 وضع التجربة: كم عدد الجلسات؟ (من 1 إلى 8)")
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
    global is_running, current_sessions, is_test_mode
    if not is_running:
        return
    tz = pytz.timezone("Africa/Algiers")
    alg_time = datetime.now(tz)
    work_duration = timedelta(minutes=5 if is_test_mode else 60)  # الجلسات
    break_duration = timedelta(minutes=2 if is_test_mode else 10)  # الاستراحات

    start_time = alg_time
    end_time = start_time + work_duration

    for i in range(1, current_sessions + 1):
        if not is_running:
            return

        msg = await bot.send_message(
            CHANNEL_ID,
            f"📅 • الجلسة {i} 📚 :\n\n"
            f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
            f"بالتوفيق والسداد للجميع 💜"
        )

        # إرسال استراحة بعد 60 دقيقة
        if i == 1:
            await asyncio.sleep(work_duration.total_seconds())  # الانتظار 60 دقيقة
            if not is_running:
                return
            await bot.send_message(
                CHANNEL_ID,
                "🪫 راحة لمدة 10 دقائق ⌛️\n\n"
                "⏰ متبقي : 10Min\n\n"
                "الأفضل أن تقضيها بعيدا عن هاتفك 💜"
            )
            await asyncio.sleep(break_duration.total_seconds())  # الانتظار 10 دقائق

        # إرسال الجلسة الثانية بعد الاستراحة
        if i != current_sessions:
            start_time += work_duration + break_duration
            end_time = start_time + work_duration

    if is_running:
        await bot.send_message(
            CHANNEL_ID,
            "🔋 انتهت الجلسات\n\nشكرا لكم على بقاءكم معي حتى الآن ربي ينجحنا و يقدرنا كاملين و لي مقراش معنا الآن يقرا معنا المرة القادمة 💜"
        )
        is_running = False

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
