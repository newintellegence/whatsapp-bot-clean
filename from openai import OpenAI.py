from openai import OpenAI
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة
load_dotenv()

# إنشاء العميل بالإصدار الجديد
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# رسالة الاختبار
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "أنت شات بوت اسمه عبده، سوداني، ساخر، خفيف دم، ما بتحب الرسميات. استخدم كلمات زي (يا زول، ساي، غايتو، بالله)، وردودك دايمًا فيها نكهة سودانية، وبإيموجي 😂."
        },
        {"role": "user", "content": "عامل شنو يا عبده؟"}
    ]
)

# طباعة الرد
print(response.choices[0].message.content)
