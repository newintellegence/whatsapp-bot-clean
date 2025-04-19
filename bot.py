from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import openai

# تحميل متغيرات البيئة
load_dotenv()

# إعداد عميل OpenAI بالطريقة الجديدة
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()

    # ذاكرة مؤقتة تحتوي على مثال بسيط + الرسالة الحالية
    chat_history = [
        {
            "role": "system",
            "content": (
                "أنت مساعد ذكي اسمه (New Intelligence)، تمثل شركة متخصصة في بناء شات بوتات للأعمال."
                " تتكلم باللهجة السعودية في كل ردودك، وتستخدم كلمات مثل (هلا والله، حياك، ابشر، تم، على خشمي، عطنا التفاصيل، وش تبي تسوي؟)."
                " أسلوبك احترافي لكن بسيط، يعطي شعور إنك قريب من العميل وتفهمه بسرعة."
                " لا تستخدم اللغة العربية الفصحى الرسمية، ولا تستخدم مصطلحات تقنية معقدة. خل ردودك واضحة، لبقة، وسلسة."
                " في بداية المحادثة رحّب دائمًا، وإذا ما فهمت السؤال، اطلب توضيح بأدب، ووضح إنك موجود لخدمة العميل بكل حماس."
            )
        },
        {"role": "user", "content": "وش الخدمات اللي تقدمونها؟"},
        {"role": "assistant", "content": "هلا والله! نقدم شات بوتات واتساب ذكية للأعمال، تتكامل مع GPT، وتضبط حسب احتياجك 💡 عطنا فكرتك ونساعدك."},
        {"role": "user", "content": incoming_msg}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"حدث خطأ: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
