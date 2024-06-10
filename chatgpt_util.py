import os
import time

import requests
import json
from dotenv import load_dotenv

load_dotenv()


def send_message(message):
    i = 2
    while True:
        try:
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message},
                    ],
                },
                headers={"Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")},
                timeout=30,
            )
            res = json.loads(res.text)["choices"][0]["message"]["content"]
            break
        except BaseException:
            time.sleep(2**i)
            i += 1

    return res
