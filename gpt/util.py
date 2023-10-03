import openai
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API")
openai.api_key = api_key

def get_reply(query: str) -> str:
    print("MESSAGE:") 
    print(query)

    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ]
    )
    print("RESPONSE: ")
    print(result.choices[0].message.content)
    return result.choices[0].message.content
