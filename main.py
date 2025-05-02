import asyncio
from datetime import datetime, timedelta
import pytz
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from keep_alive import keep_alive

# إعدادات البوت
TOKEN = "7700309780:AAFVb4k6AwrWKQMidbtjoRNrEsu3vOcb06c"
CHANNEL_ID = -1002333575329  # غيّره إذا لزم

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

# الحالات
class SessionStates(StatesGroup):
    waiting_for_count = State()
    waiting_for_test_count = State()

# متغيرات التحكم
is_running = False
is_test_mode = False

# /start العادية
@dp.message(F.text == "/start")
async def handle_start(message: Message, state: FSMContext):
    global is_running, is_test_mode
    if is_running:
        await message.answer("⚠️ الجلسات تعمل بالفعل!")
        return
    is_test_mode = False
    await message.answer("كم عدد الجلسات التي تريد تشغيلها؟ (من 1 إلى 8)")
    await state.set_state(SessionStates.waiting_for_count)

# /test وضع التجربة
@dp.message(F.text == "/test")
async def handle_test(message: Message, state: FSMContext):
    global is_running, is_test_mode
    if is_running:
        await message.answer("⚠️ الجلسات تعمل بالفعل!")
        return
    is_test_mode = True
    await message.answer("🔎 وضع التجربة: كم عدد الجلسات؟ (من 1 إلى 8)")
    await state.set_state(SessionStates.waiting_for_test_count)

# استلام عدد الجلسات في الوضع العادي والتجريبي
@dp.message(SessionStates.waiting_for_count)
@dp.message(SessionStates.waiting_for_test_count)
async def handle_count(message: Message, state: FSMContext):
    global is_running
    try:
        count = int(message.text)
        if count < 1 or count > 8:
            await message.answer("⚠️ أدخل رقمًا من 1 إلى 8.")
            return
        is_running = True
        await message.answer("✅ بدأ إرسال الجلسات...")
        await state.clear()
        await send_sessions(count)
    except ValueError:
        await message.answer("⚠️ الرجاء إدخال رقم صحيح من 1 إلى 8.")

# أمر الإيقاف
@dp.message(F.text == "/stop")
async def stop_sessions(message: Message):
    global is_running
    if is_running:
        is_running = False
        await message.answer("⛔️ تم إيقاف الجلسات.")
    else:
        await message.answer("لا توجد جلسات حالياً لإيقافها.")

# الدالة الرئيسية لإرسال الجلسات
async def send_sessions(total_sessions):
    global is_running, is_test_mode

    # التوقيت حسب الجزائر
    tz = pytz.timezone("Africa/Algiers")
    now = datetime.now(tz)

    # تحديد المدة حسب الوضع
    work_duration = timedelta(minutes=3 if is_test_mode else 60)
    break_duration = timedelta(minutes=1 if is_test_mode else 10)

    for i in range(1, total_sessions + 1):
        if not is_running:
            return

        start_time = datetime.now(tz)
        end_time = start_time + work_duration

        # إرسال جلسة
        await bot.send_message(
            CHANNEL_ID,
            f"📅 • الجلسة {i} 📚 :\n\n"
            f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
            f"بالتوفيق والسداد للجميع 💜"
        )

        await asyncio.sleep(work_duration.total_seconds())
        if not is_running:
            return

        # استراحة (ماعدا بعد آخر جلسة)
        if i != total_sessions:
            await bot.send_message(
                CHANNEL_ID,
                "🪫 راحة الآن ⌛️\n\n"
                "⏳ حاول الابتعاد عن الهاتف قليلاً."
            )
            await asyncio.sleep(break_duration.total_seconds())

    # نهاية كل الجلسات
    if is_running:
        await bot.send_message(
            CHANNEL_ID,
            "🔋 انتهت الجلسات\n\n"
            "شكراً على المتابعة! ربي ينجحنا كاملين 💜"
        )
        is_running = False

# تشغيل البوت
async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
