from google import genai
from google.genai import types
from openai import OpenAI

from crawl4ai import LLMConfig

import os
from dotenv import load_dotenv

from .model import Model


"""
    refactor to openai versoin
"""


class Gemini(Model):
    def __init__(self, model):
        load_dotenv(override=True)
        self.api_key = os.getenv("GEMINI_API")
        self.model = model
        self.client = genai.Client(api_key=self.api_key)
        self.messages = self.client.chats.create(model=model)

    def clear_message(self):
        self.messages = self.client.chats.create(model=self.model)

    def set_api(self, api):
        self.api = api

    def completion(self, query: str):
        res = self.message.send_message(query)
        return res.text

    def reset(self):
        """
        Reset chat message
        """
        self.message = self.client.chats.create(model=Model)

    def add_system_instruction(self, instruction: str):
        self.message.send_message(
            config=types.GenerateContentConfig(system_instruction=instruction)
        )

    def get_client(self):
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return client

    def get_llm_config(self) -> LLMConfig:
        return LLMConfig(provider="gemini/" + self.model, api_token=self.api_key)

    def get_model(self):
        return self.model
