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

TOKEN = "YOUR_BOT_TOKEN"
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

async def countdown_edit(msg, total_seconds):
    for remaining in range(total_seconds // 60, 0, -1):
        if not is_running:
            return
        try:
            await asyncio.sleep(60)
            lines = msg.text.split("\n")
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("⏰ متبقي"):
                    lines[i] = f"⏰ متبقي : {remaining}Min"
                    updated = True
                    break
            if not updated:  # أضف السطر بعد السطر الأخير الخاص بالتوقيت
                for i, line in enumerate(lines):
                    if "إلى" in line:
                        lines.insert(i + 1, f"⏰ متبقي : {remaining}Min")
                        break
            new_text = "\n".join(lines)
            await bot.edit_message_text(new_text, msg.chat.id, msg.message_id)
        except Exception as e:
            break

    # إذا انتهى الوقت ولم يتم تحديث الرسالة في الدورة، يمكننا تحديد حالة الانتهاء
    if total_seconds == 0 or remaining <= 0:
        lines = msg.text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("⏰ متبقي"):
                lines[i] = "⏰ الجلسة انتهت"
                break
        new_text = "\n".join(lines)
        await bot.edit_message_text(new_text, msg.chat.id, msg.message_id)

async def send_sessions():
    global is_running, current_sessions, is_test_mode
    if not is_running:
        return
    tz = pytz.timezone("Africa/Algiers")
    alg_time = datetime.now(tz)
    work_duration = timedelta(minutes=5 if is_test_mode else 60)
    break_duration = timedelta(minutes=2 if is_test_mode else 10)

    start_time = alg_time
    end_time = start_time + work_duration
    msg = await bot.send_message(CHANNEL_ID,
        f"🫶 بسم الله نبدا على بركة الله\n\n"
        f"📅 • الجلسة الأولى 📚 :\n\n"
        f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
        f"بالتوفيق والسداد للجميع 💜")
    await countdown_edit(msg, int(work_duration.total_seconds()))
    await asyncio.sleep(work_duration.total_seconds())

    if not is_running:
        return

    msg = await bot.send_message(CHANNEL_ID,
        "🪫 راحة لمدة 10 دقائق ⌛️\n\n"
        "⏰ متبقي : 10Min\n\n"
        "الأفضل أن تقضيها بعيدا عن هاتفك 💜")
    await countdown_edit(msg, int(break_duration.total_seconds()))
    await asyncio.sleep(break_duration.total_seconds())

    for i in range(2, current_sessions + 1):
        if not is_running:
            return
        start_time += work_duration + break_duration
        end_time = start_time + work_duration

        msg = await bot.send_message(CHANNEL_ID,
            f"📅 • الجلسة {i} 📚 :\n\n"
            f"🕥   • من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n\n"
            f"بالتوفيق والسداد للجميع 💜")
        await countdown_edit(msg, int(work_duration.total_seconds()))
        await asyncio.sleep(work_duration.total_seconds())

        if i != current_sessions:
            if not is_running:
                return
            msg = await bot.send_message(CHANNEL_ID,
                "🪫 راحة لمدة 10 دقائق ⌛️\n\n"
                "⏰ متبقي : 10Min\n\n"
                "الأفضل أن تقضيها بعيدا عن هاتفك 💜")
            await countdown_edit(msg, int(break_duration.total_seconds()))
            await asyncio.sleep(break_duration.total_seconds())

    if is_running:
        await bot.send_message(CHANNEL_ID,
            "🔋 انتهت الجلسات\n\nشكرا لكم على بقاءكم معي حتى الآن ربي ينجحنا و يقدرنا كاملين و لي مقراش معنا الآن يقرا معنا المرة القادمة 💜")
        is_running = False

async def main():
    keep_alive()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
