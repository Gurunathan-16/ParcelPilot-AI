import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")

print("Key found:", bool(key))
print("Key prefix:", key[:8] if key else None)

client = Groq(api_key=key)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Say ParcelPilot is working."
        }
    ]
)

print(response.choices[0].message.content)