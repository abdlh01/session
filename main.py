from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import pytz
import asyncio

# إعدادات البوت
TOKEN = "YOUR_BOT_TOKEN"  # استبدل بـ Token الخاص بك
CHANNEL_ID = -1002333575329  # استبدل برقم القناة الخاصة بك

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(bot)

# إعداد الجلسات
def create_sessions(total_sessions):
    sessions = []
    tz = pytz.timezone("Africa/Algiers")
    work_duration = timedelta(minutes=60)  # مدة الجلسة
    break_duration = timedelta(minutes=10)  # مدة الراحة
    
    for i in range(1, total_sessions + 1):
        start_time = datetime.now(tz) + timedelta(minutes=(i-1)*70)  # تحديد وقت الجلسة
        end_time = start_time + work_duration

        session_text = f"📅 الجلسة {str(i).zfill(2)} 📚 :\n" \
                       f"🕥 من {start_time.strftime('%H:%M')} إلى {end_time.strftime('%H:%M')}\n" \
                       "بالتوفيق والسداد للجميع 💜\n\n"
        
        sessions.append(session_text)
        
        if i != total_sessions:  # إذا كانت ليست الجلسة الأخيرة
            sessions.append("🪫 راحة لمدة 10 دقائق ⌛️\n\n" 
                             "الأفضل أن تقضيها بعيدًا عن هاتفك 💜\n\n")
    
    return "\n".join(sessions)

# جدولة إرسال الجلسات
async def send_all_sessions():
    total_sessions = 5  # عدد الجلسات
    sessions_text = create_sessions(total_sessions)

    # تحديد وقت إرسال الرسائل
    send_time = datetime.now(pytz.timezone("Africa/Algiers")) + timedelta(seconds=10)  # مثال: إرسال بعد 10 ثوانٍ

    # استخدام APScheduler لجدولة إرسال الرسائل
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        bot.send_message,
        DateTrigger(run_date=send_time),  # تحديد وقت الإرسال
        args=[CHANNEL_ID, sessions_text]
    )
    scheduler.start()

# تشغيل البوت
async def main():
    await send_all_sessions()  # جدولة إرسال الرسائل
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
