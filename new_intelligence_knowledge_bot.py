
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# محتوى الخدمة كنص عادي
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

# تجزئة النص إلى مقاطع صغيرة
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents([Document(page_content=knowledge_text)])

# بناء قاعدة المعرفة باستخدام FAISS
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = FAISS.from_documents(docs, embedding)

# إعداد نموذج الأسئلة والإجابات
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# تجربة سؤال
question = input("اسأل عن الخدمة: ")
answer = qa.run(question)
print("\nالرد من قاعدة المعرفة:")
print(answer)
