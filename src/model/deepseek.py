from .model import Model

from openai import OpenAI
from dotenv import load_dotenv

from crawl4ai import LLMConfig

import os


class Deepseek(Model):
    def __init__(self, model, api_key: str = ""):
        load_dotenv(override=True)
        self.api_key = os.getenv("DEEPSEEK_API") if api_key == "" else api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.messages = []

    def set_api(self, api_key: str):
        self.api_key = api_key

    def completion(self, query):
        self._add_message(query)
        response = self.client.chat.completions.create(
            model=self.model, messages=self.messages, stream=False
        )
        return response.choices[0].message.content

    def add_system_instructuion(self, instruction: str):
        pass

    def get_llm_config(self):
        return LLMConfig(provider="deepseek/" + self.model, api_token=self.api_key)

    def get_client(self):
        return self.client

    def get_model(self):
        return self.model

    def clear_message(self):
        self.messages = []

    def _add_message(self, message, role="use"):
        self.messages.append({"role": "user", "content": message})

    def completion_stream(self, message):
        self._add_message(message=message, role="user")
        stream = self.client.chat.completions.create(
            model=self.model, messages=self.messages, stream=True
        )
        for event in stream:
            text_chunk = getattr(event.choices[0].delta, "content", None)
            if text_chunk:
                yield text_chunk
