
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import openai

# قاعدة المعرفة
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document

# تحميل متغيرات البيئة
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
user_sessions = {}

# إعداد قاعدة المعرفة
knowledge_text = """
أنا عبدالرحمن، مقدم خدمة New Intelligence المتخصصة في تصميم شات بوتات واتساب ذكية للأعمال.
أساعد العيادات، المتاجر، والجمعيات في أتمتة التواصل مع العملاء باللهجة السعودية.

🔹 ما نقدمه:
- إنشاء بوت واتساب مخصص باستخدام Python + Flask
- تكامل مع ChatGPT (OpenAI API) لتقديم ردود ذكية
- ربط مع Twilio لاستقبال الرسائل والرد تلقائياً
- نشر البوت على الإنترنت باستخدام Render أو n8n
- تخصيص نغمة البوت لتكون احترافية وباللهجة السعودية

🔹 الخطط والأسعار:
1. إعداد بوت بسيط باستخدام n8n — من 150 إلى 300 ريال
2. إعداد بوت ذكي بـ Python — من 400 إلى 1500 ريال
3. دعم شهري (تحديثات + صيانة + مراقبة) — من 50 إلى 400 ريال

🔹 مميزات البوت:
- يتكلم بلهجة سعودية لبقة (مثل: حياك، هلا والله، ابشر)
- يرد بسرعة واحترافية على استفسارات العملاء
- يقترح حلول وينفذ أوامر تلقائية
- قابل للتطوير والربط مع قواعد معرفة مخصصة

📞 للتواصل:
رقم الجوال: 0568604393
البريد الإلكتروني: newstats25@gmail.com
"""

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents([Document(page_content=knowledge_text)])
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = FAISS.from_documents(docs, embedding)

qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    user_number = request.values.get("From", "")

    # تجهيز الجلسة
    if user_number not in user_sessions:
        user_sessions[user_number] = []

    # إذا اختار المستخدم باقة محددة، نحفظها في الذاكرة
    if "باقة متوسطة" in incoming_msg:
        user_sessions[user_number].append({"role": "system", "content": "المستخدم اختار باقة متوسطة"})

    elif "باقة بسيطة" in incoming_msg:
        user_sessions[user_number].append({"role": "system", "content": "المستخدم اختار باقة بسيطة"})

    elif "باقة ذكية" in incoming_msg:
        user_sessions[user_number].append({"role": "system", "content": "المستخدم اختار باقة ذكية"})

    # إضافة الرسالة للذاكرة
    user_sessions[user_number].append({"role": "user", "content": incoming_msg})

    # إعداد السياق مع system prompt محسّن
    chat_history = [
        {
            "role": "system",
            "content": (
                "أنت مساعد ذكي تمثل New Intelligence. تجاوب باللهجة السعودية بأسلوب احترافي وبسيط."
                " إذا كان المستخدم سأل من قبل عن باقة أو خدمة، لا تكرر الترحيب. خلك واعي بالسياق ورد بناءً عليه."
                " استخدم كلمات مثل (تم، تمام، عطنا، ابشر) بدون تكرار (هلا والله) في كل رد."
            )
        }
    ] + user_sessions[user_number]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history
        )
        reply = response.choices[0].message.content
        user_sessions[user_number].append({"role": "assistant", "content": reply})

        if len(user_sessions[user_number]) > 10:
            user_sessions[user_number] = user_sessions[user_number][-10:]

    except Exception as e:
        reply = f"صار خطأ: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
