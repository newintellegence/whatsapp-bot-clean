from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import openai
import json
from pathlib import Path

# تحميل متغيرات البيئة
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# إعداد مجلد الجلسات
session_dir = Path("sessions")
session_dir.mkdir(exist_ok=True)
user_sessions = {}

# قاعدة المعرفة الخاصة بخدمتك
knowledge_base = """
أنا مساعدك عبدالرحمن . أقدم شات بوتات واتساب ذكية للعيادات، المتاجر، وغيرها.
الخدمات المتوفرة:
- إعداد بوت واتساب ذكي باستخدام GPT.
- ربط مع Twilio وخدمات النشر على Render.
- الباقات تبدأ من 399 ريال، والدعم الشهري حسب احتياجك.

للتواصل: 0568604393
بريد: newstats25@gmail.com
"""

# رد الأسعار المخصص
price_reply = """
📋 **تفاصيل الباقات المتوفرة:**
🔥 باقات New Intelligence – شغّل ذكاءك تلقائيًا
🟢 NI Start – باقة الانطلاقة
"للي يبغى يدخل عالم الأتمتة بأبسط شكل"

🔧 التركيب: 599 ريال (مرة واحدة)
💳 الاشتراك الشهري: 399 ريال
✅ ردود فورية بالذكاء الاصطناعي
✅ لغة واحدة
⛔️ بدون ذاكرة
⛔️ بدون تخصيص

⭐ NI Smart – الباقة الذهبية (الأكثر طلبًا)
"ذكية، مخصصة، وتفهم عملاءك"

🔧 التركيب: 799 ريال
💳 الاشتراك الشهري: 599 ريال
✅ دعم لغتين (عربي + إنجليزي)
✅ شخصية مخصصة باللهجة والأسلوب
✅ ذاكرة جلسة (مؤقتة)
✅ أزرار تفاعلية / قوائم
✅ تقارير محادثات دورية
✅ استضافة Render
✅ رقم واتساب رسمي

🧠 NI Pro+ – باقة الذكاء الكامل
"للي يبغى بوت فعليًا يشتغل بداله"

🔧 التركيب: 1499 ريال
💳 الاشتراك الشهري: 999 ريال
✅ ذاكرة حقيقية (Real Session Memory)
✅ تكامل Google Sheets أو قاعدة بيانات
✅ استقبال صور/ملفات/صوت
✅ تحليل المحادثات
✅ لوحة تحكم داخلية
✅ ربط مع نظام عملك إن وجد (CRM – حجوزات – بيانات)
✅ دعم مخصص وأولوية
✅ استضافة متقدمة
✅ رقم واتساب رسمي

💬 إذا حاب تعرف أي باقة أنسب لك أو تحتاج شرح أكثر، عطنا تفاصيل نشاطك وابشر!
"""

# الكلمات المفتاحية لفلتر الأسعار
price_keywords = ["سعر", "تكلفة", "باقات", "اشتراك", "الخطة", "الباقات"]

# Flask App
app = Flask(__name__)

def save_session(user_number, session_data):
    session_path = session_dir / f"session_{user_number.replace('+', '')}.json"
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    user_number = request.values.get("From", "")

    if user_number not in user_sessions:
        user_sessions[user_number] = []

    user_sessions[user_number].append({"role": "user", "content": incoming_msg})

    # فلتر السعر
    if any(keyword in incoming_msg for keyword in price_keywords):
        reply = price_reply
    else:
        # إعداد شخصية البوت
        system_message = (
            "أنت مساعد ذكي اسمك عبدالرحمن. "
            "تتكلم سعودي: هلا، حياك، أبشر، تم، وش تبي؟، عطني تفاصيلك. "
            "لا ترد بلهجات أو لغات غير سعودية. "
            "ركز على: تركيب بوت واتساب، الأسعار، والدعم فقط. "
            "ردودك بسيطة وسريعة، بدون تعقيد. "
            "تكلم كأنك تخدم زبون محلي وتبي تسهّل عليه. "
            "لا تذكر خدمات غير البوت. "
            f"معلومات:\n{knowledge_base}\n"
            "ابدأ كل محادثة بتعريف بسيط إذا أول تواصل."
        )

        

        chat_history = [{"role": "system", "content": system_message}] + user_sessions[user_number]

        try:
            response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=chat_history,
    temperature=0.3  # كان 0.7
        )
            
            reply = response.choices[0].message.content
            user_sessions[user_number].append({"role": "assistant", "content": reply})

            if len(user_sessions[user_number]) > 10:
                user_sessions[user_number] = user_sessions[user_number][-10:]

            save_session(user_number, user_sessions[user_number])

        except Exception as e:
            reply = f"صار خطأ: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
