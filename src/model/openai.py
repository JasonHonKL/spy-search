from .model import Model
from ..utils import read_config

from openai import OpenAI as openai
from dotenv import load_dotenv

from crawl4ai import LLMConfig

import os

import logging

logger = logging.getLogger(__name__)


class OpenAI(Model):
    def __init__(self, model: str = "", api_key: str = ""):
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENAI_API_KEY")

        config = read_config()
        if config.get("base_url", "") == "":
            self.client = openai(
                api_key=self.api_key,
            )
        else:
            self.client = openai(
                api_key=self.api_key, base_url=config.get("base_url", "")
            )

        self.model = model
        self.messages = []

    def set_api(self, api_key: str):
        self.api_key = api_key

    def completion(self, query):
        self._add_message(query)
        response = self.client.chat.completions.create(
            model=self.model, messages=self.messages, stream=False
        )
        while not response.choices:
            response = self.client.chat.completions.create(
                model=self.model, messages=self.messages, stream=False
            )
        return response.choices[0].message.content

    def completion_stream(self, message):
        self._add_message(message=message, role="user")

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
                temperature=0.7,
                extra_body={
                    "provider": {
                        "allow_fallbacks": True
                    }
                }
            )

            buffer = []
            buffer_size = 3  # smaller buffer for faster yield

            for event in stream:
                if not event.choices:
                    continue

                choice = event.choices[0]

                if hasattr(choice, "finish_reason") and choice.finish_reason:
                    if buffer:
                        yield "".join(buffer)
                    break

                content = getattr(choice.delta, "content", None)
                if content:
                    buffer.append(content)

                    if len(buffer) >= buffer_size:
                        yield "".join(buffer)
                        buffer = []

            if buffer:
                yield "".join(buffer)

        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise

    def add_system_instructuion(self, instruction: str):
        pass

    def get_llm_config(self):
        return LLMConfig(provider="openai/" + self.model, api_token=self.api_key)

    def get_client(self):
        return self.client

    def get_model(self):
        return self.model

    def clear_message(self):
        self.messages = []

    def _add_message(self, message, role="user"):
        max_history = 20
        self.messages.append({"role": role, "content": message})
        if len(self.messages) > max_history:
            self.messages = self.messages[-max_history:]
