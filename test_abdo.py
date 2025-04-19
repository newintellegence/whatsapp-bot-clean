from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "أنت شات بوت سوداني ساخر ودمك خفيف 😂. اسمك عبده، ما بتحب الرسميات وبتتكلم زي كأنك صاحب الزول. بتقول كلمات زي (يا زول، ساي، غايتو، بالله)."
        },
        {"role": "user", "content": "عامل شنو يا عبده؟"}
    ]
)

print(response.choices[0].message.content)
