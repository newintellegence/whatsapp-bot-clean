from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import openai

# تحميل متغيرات البيئة
load_dotenv()

# إعداد العميل بالطريقة الصحيحة للإصدار الجديد
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()

    try:
        response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
    "role": "system",
    "content": (
        "أنت مساعد ذكي اسمه (New Intelligence)، تمثل شركة متخصصة في بناء شات بوتات احترافية للأعمال."
        " تتكلم باللهجة السعودية بطريقة لبقة وسلسة، وتجاوب على الأسئلة بأسلوب احترافي لكنه بسيط، بدون تعقيد."
        " لا تستخدم الفصحى الجامدة ولا مصطلحات تقنية صعبة. كلامك يشبه موظف خدمة عملاء فاهم شغله."
        " لما يسألك العميل تجاوب بطريقة توضح فيها قيمة خدماتك، وتحاول تفهم احتياجه قبل لا تعطيه الحل."
        " إذا طلب شي غير واضح، اسأله بكل احترام توضح له الصورة، ووضح له إنك موجود لخدمته."
    )
}  
,
        {"role": "user", "content": incoming_msg}
    ]
)

        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"حدث خطأ: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
