import os
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.environ['MODEL_PROXY_API_KEY'],
    base_url='https://mp-staging.kaggle.net/models/openapi'
)

models = [
    'gemini-2.5-pro',
    'google/gemini-2.5-pro',
    'gemini-3.5-flash',
    'google/gemini-3.5-flash',
    'gpt-5.4-2026-03-05',
    'openai/gpt-5.4-2026-03-05',
    'claude-sonnet-4-6-default',
    'anthropic/claude-sonnet-4-6-default',
]

for m in models:
    print(f"Testing {m}...")
    try:
        response = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)
