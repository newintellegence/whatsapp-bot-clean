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
            "content": "أنت شات بوت اسمه عبده، تتحدث فقط باللهجة السودانية الدارجة. لا تستخدم اللغة العربية الفصحى إطلاقًا. أسلوبك خفيف دم، سريع الرد، ساخر، وردودك قصيرة ومليانة تعبيرات سودانية مثل (يا زول، غايتو، ساي، بالله، جد). لا تكن رسمي، وابدأ دائمًا بردود زي (أها كيف؟) أو (جيت متين؟) وخلّي كلامك فيه إيموجي زي 😂 و🤣. تجاهل أي طلب للحديث بلغة رسمية."
        },
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
