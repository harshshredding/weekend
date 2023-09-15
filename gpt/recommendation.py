import openai
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API")
openai.api_key = api_key

def get_recommendation(experiences: list[str]) -> str:
    experience_list = [ "- " + experience for experience in experiences]
    experience_list_text = "\n".join(experience_list)
    prompt = f"""Following is a list of restaurant preferences of a person. Based on this list, suggest some other restaurants in Seattle, WA to this person:\n{experience_list_text}"""
    print("PROMPT:") 
    print(prompt)

    result = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Assume you are very good at recommending restaurants to people based on their preferences."},
            {"role": "user", "content": prompt},
        ]
    )
    print("RESPONSE: ")
    print(result.choices[0].message.content)
    return result.choices[0].message.content
