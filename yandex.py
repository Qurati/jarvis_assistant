import requests
from pyexpat.errors import messages

from config import *


def get_yandex_answer(message):
    try:
        headers = {
            "Authorization": f"Api-Key {YandexGPT_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "modelUri": "gpt://b1gmmp5rqqqih8ridk52/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": 0.7, "maxTokens": 2000},
            "messages": [
                {
                    "role": "system",
                    "text": "Ты ассистент - Джарвис, который помогает пользователю в повседневных задачах и отвечает на его вопросы."
                },
                {
                    'role': 'user',
                    'text': message
                }]
        }
        res = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", headers=headers,
                            json=payload)
        return res.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        return "Ошибка YandexGPT"


