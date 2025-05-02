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
TOKEN = "7700309780:AAE1NunbggnimpxpVJB6QNA1F7UJo3-Bfvc"
CHANNEL_ID = -1002333575329  # غيّره إذا لزم
PASSWORD = "1802"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

# الحالات
class SessionStates(StatesGroup):
    waiting_for_count = State()
    waiting_for_test_count = State()
    waiting_for_password = State()
    waiting_for_stop_password = State()

# متغيرات التحكم
is_running = False
is_test_mode = False
pending_count = 0

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

# استلام عدد الجلسات
@dp.message(SessionStates.waiting_for_count)
@dp.message(SessionStates.waiting_for_test_count)
async def handle_count(message: Message, state: FSMContext):
    global pending_count
    try:
        count = int(message.text)
        if count < 1 or count > 8:
            await message.answer("⚠️ أدخل رقمًا من 1 إلى 8.")
            return
        pending_count = count
        await message.answer("🔐 من فضلك أدخل كلمة المرور لتأكيد تشغيل الجلسات:")
        await state.set_state(SessionStates.waiting_for_password)
    except ValueError:
        await message.answer("⚠️ الرجاء إدخال رقم صحيح من 1 إلى 8.")

# التحقق من كلمة المرور قبل التشغيل
@dp.message(SessionStates.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    global is_running, pending_count
    if message.text != PASSWORD:
        await message.answer("❌ كلمة المرور خاطئة.")
        return
    is_running = True
    await message.answer("✅ تم التحقق! بدأ إرسال الجلسات...")
    await state.clear()
    await send_sessions(pending_count)

# أمر الإيقاف
@dp.message(F.text == "/stop")
async def stop_sessions(message: Message, state: FSMContext):
    global is_running
    if not is_running:
        await message.answer("لا توجد جلسات حالياً لإيقافها.")
        return
    await message.answer("🔐 من فضلك أدخل كلمة المرور لإيقاف الجلسات:")
    await state.set_state(SessionStates.waiting_for_stop_password)

@dp.message(SessionStates.waiting_for_stop_password)
async def confirm_stop(message: Message, state: FSMContext):
    global is_running
    if message.text != PASSWORD:
        await message.answer("❌ كلمة المرور خاطئة.")
        return
    is_running = False
    await state.clear()
    await message.answer("⛔️ تم إيقاف الجلسات.")

# الدالة الرئيسية لإرسال الجلسات
async def send_sessions(total_sessions):
    global is_running, is_test_mode

    tz = pytz.timezone("Africa/Algiers")
    work_duration = timedelta(minutes=3 if is_test_mode else 60)
    break_duration = timedelta(minutes=1 if is_test_mode else 10)

    for i in range(1, total_sessions + 1):
        if not is_running:
            return

        start_time = datetime.now(tz)
        end_time = start_time + work_duration

        header = "🫶  بسم الله نبدا على بركة الله\n\n" if i == 1 else ""
        await bot.send_message(
            CHANNEL_ID,
            f"{header}📅 • الجلسة {str(i).zfill(2)} 📚 :\n\n"
            f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
            f"بالتوفيق والسداد للجميع 💜"
        )

        await asyncio.sleep((end_time - datetime.now(tz)).total_seconds())

        if not is_running:
            return

        if i != total_sessions:
            await bot.send_message(
                CHANNEL_ID,
                "🪫 راحة لمدة 10 دقائق ⌛️\n\n"
                "الأفضل أن تقضيها بعيدا عن هاتفك 💜"
            )
            await asyncio.sleep(break_duration.total_seconds())

    if is_running:
        await bot.send_message(
            CHANNEL_ID,
            "🔋 انتهت الجلسات\n\n"
            "🫶 شكرا لكم على بقاءكم معنا حتى الآن بوركت جهودكم ومساعيكم\n\n"
            "🎀 و لي مقراش معنا الآن يقرا معنا في الجلسات القادمة 💜"
        )
        is_running = False

# تشغيل البوت
async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
