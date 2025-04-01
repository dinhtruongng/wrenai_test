import os

import litellm
from dotenv import load_dotenv

load_dotenv(dotenv_path="docker/.env")
API_KEY_NAME = "MONICA_API_KEY"

response = litellm.completion(
    model="openai/gpt-4o-mini",  # add `openai/` prefix to model so litellm knows to route to OpenAI
    api_key=os.environ.get(API_KEY_NAME),  # api key to your openai compatible endpoint
    api_base="https://openapi.monica.im/v1",  # set API Base of your Custom OpenAI Endpoint
    messages=[
        {
            "role": "user",
            "content": "Hey, how's it going?",
        }
    ],
)
print(response)
