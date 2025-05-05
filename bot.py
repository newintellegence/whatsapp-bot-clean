from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
print("CWD =", os.getcwd())
import openai
import json
from pathlib import Path

# **إضافات Google Sheets**
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# تحميل متغيرات البيئة
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- إعداد Google Sheets API باستخدام ملف الاعتماديات أو المتغيّر البيئي ---
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# استخدم متغيّر البيئة أولًا، وإذا لم يُعرّف استخدم الملف المحلي
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or 'google_cred.json'
print("GOOGLE_APPLICATION_CREDENTIALS =", cred_path)
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)

client_gs = gspread.authorize(creds)
sheet = client_gs.open('Appointments').sheet1
# **انتهت إضافات Google Sheets**

# إعداد مجلد الجلسات
session_dir = Path("sessions")
session_dir.mkdir(exist_ok=True)
user_sessions = {}

# قاعدة المعرفة الخاصة بخدمتك
knowledge_base = """
أنا مساعدك عبدالرحمن. أقدم شات بوتات واتساب ذكية للعيادات، المتاجر، والجمعيات.
الخدمات:
- إعداد بوت واتساب ذكي باستخدام GPT.
- ربط مع Twilio وخدمات النشر على Render.
- الباقات تبدأ من 599 ريال شهريًا، حسب احتياج العميل.

للتواصل: 0568604393
0568995120
البريد: newstats25@gmail.com
"""

price_keywords = ["سعر", "تكلفة", "باقات", "اشتراك", "الخطة", "الباقات"]

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

    # جلسة التجربة
    session_file = session_dir / f"trial_{user_number.replace('+', '')}.json"
    trial_data = {}

    if session_file.exists():
        with open(session_file, 'r', encoding="utf-8") as f:
            trial_data = json.load(f)

    if incoming_msg.lower() == "تجربه" and not trial_data.get("trial_active"):
        trial_data["trial_active"] = True
        trial_data["awaiting_business_name"] = True
        save_trial_session(session_file, trial_data)
        resp = MessagingResponse()
        resp.message("🎯 مرحباً بك في النسخة التجريبية!\nمن فضلك، ما اسم النشاط التجاري الخاص بك؟")
        return str(resp)

    if trial_data.get("trial_active"):
        resp = MessagingResponse()

        if trial_data.get("awaiting_business_name"):
            trial_data["business_name"] = incoming_msg
            trial_data["awaiting_business_name"] = False
            trial_data["awaiting_client_name"] = True
            save_trial_session(session_file, trial_data)
            resp.message(f"جميل! سجلت اسم نشاطك كـ *{incoming_msg}*.\nوالحين، ممكن اسمك؟")
            return str(resp)

        elif trial_data.get("awaiting_client_name"):
            trial_data["client_name"] = incoming_msg
            trial_data["awaiting_client_name"] = False
            trial_data["awaiting_appointment_confirm"] = True
            save_trial_session(session_file, trial_data)
            resp.message(
                f"مرحباً *{incoming_msg}* 👋\n"
                f"أنا موظف خدمة العملاء من *{trial_data['business_name']}*.\n"
                "هل تريد حجز موعد؟"
            )
            return str(resp)

        # **حجز الموعد: التأكيد**
        elif trial_data.get("awaiting_appointment_confirm"):
            if incoming_msg in ["نعم", "yes", "أكيد", "ابشر"]:
                trial_data["awaiting_appointment_confirm"] = False
                trial_data["awaiting_appointment_datetime"] = True
                save_trial_session(session_file, trial_data)
                resp.message("حلو، من فضلك ارسل لي التاريخ والوقت اللي يناسبك مثل: 2025-04-30 10:00")
            else:
                trial_data["trial_active"] = False
                save_trial_session(session_file, trial_data)
                resp.message("تمام، إذا احتجت أي شيء آخر خبرني.")
            return str(resp)

        # **حجز الموعد: استقبال التاريخ والوقت**
        elif trial_data.get("awaiting_appointment_datetime"):
            trial_data["appointment_datetime"] = incoming_msg
            trial_data["awaiting_appointment_datetime"] = False
            save_trial_session(session_file, trial_data)

            # أضف الصف إلى Google Sheets
            sheet.append_row([
                user_number,
                trial_data["business_name"],
                trial_data["client_name"],
                trial_data["appointment_datetime"]
            ])

            resp.message(f"✅ تم حجز موعدك يوم {trial_data['appointment_datetime']}.\nسوف نؤكد لك قريباً.")
            trial_data["trial_active"] = False
            save_trial_session(session_file, trial_data)
            return str(resp)

        else:
            # GPT في وضع التجربة مع System Message مختصر لتوفير التوكنز
            trial_system_message = (
                f"أنت موظف خدمة عملاء في عيادة وهمية اسمها *{trial_data['business_name']}*.\n"
                f"ردودك واقعية باللهجة السعودية، ولا تذكر أنك بوت أو هذا وضع تجريبي.\n"
                f"إذا سألك عن مواعيد الدوام، قل يبدأ من 9 صباحاً حتى 11 مساءً.\n"
                f"إذا سألك عن الخدمات، اذكر خدمات أسنان مثل تنظيف، تبييض، زراعة.\n"
                f"إذا سألك عن الموقع، قل حي العليا، الرياض.\n"
                f"كن مختصرًا ولا تستخدم أكثر من 30 كلمة في الرد."
            )

            trial_chat = [
                {"role": "system", "content": trial_system_message},
                {"role": "user", "content": incoming_msg}
            ]

            try:
                gpt_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=trial_chat,
                    temperature=0.5,
                    max_tokens=100
                )
                trial_reply = gpt_response.choices[0].message.content
                resp.message(f"[تجريبي] {trial_reply}")
            except Exception as e:
                resp.message(f"[تجريبي] صار خطأ أثناء التجربة: {str(e)}")
            return str(resp)

    # الوضع العادي خارج التجربة
    user_sessions[user_number].append({"role": "user", "content": incoming_msg})

    system_message = (
        "أنت مساعد ذكي تمثل خدمة New Intelligence. "
        "تتكلم باللهجة السعودية: هلا، حياك، أبشر، تم، عطنا التفاصيل. "
        "لا تستخدم الفصحى، ولا تذكر خدمات غير تركيب بوت واتساب. "
        "ردودك ودودة وسريعة، تخدم الزبون كأنك تعرفه شخصياً. "
        "في حال سُئلت عن الأسعار أو الباقات، وضح الأسعار المذكورة بمساعدة المعرفة. "
        f"معلومات الخدمة:\n{knowledge_base}\n"
        " ابدأ كل محادثة بتعريف بسيط إذا أول تواصل. وقل كيف اقدر اخدمك"
    )

    chat_history = [{"role": "system", "content": system_message}] + user_sessions[user_number]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            temperature=0.7
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

def save_trial_session(path, data):
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    app.run(debug=True)