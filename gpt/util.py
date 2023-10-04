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


def convert_to_chatgpt_messages(messages: list[dict]):
    ret = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    for message in messages:
        if message['type'] == 'request':
            ret.append(
                {"role": "user", "content": message["content"]}
            )
        elif message['type'] == 'response':
            ret.append(
                {"role": "assistant", "content": message["content"]}
            )
        else:
            raise RuntimeError(f"invalid message type: {message['type']}")
    assert ret[-1]["role"] == "user"
    return ret



def get_reply_multiple_messages(messages: list[dict]) -> str:
    print("MESSAGES")
    for message in messages:
        print(message)
    print()

    chatgpt_messages = convert_to_chatgpt_messages(messages)
    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chatgpt_messages
    )
    print("RESPONSE: ")
    print(result.choices[0].message.content)
    return result.choices[0].message.content
