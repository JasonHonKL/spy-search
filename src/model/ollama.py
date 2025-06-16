from .model import Model
from openai import OpenAI

from ollama import chat
from crawl4ai import LLMConfig


class Ollama(Model):
    def __init__(self, model: str):
        self.model = model
        self.messages = []

    def set_api(self, api):
        """
        no need to do anything
        """
        return

    def completion(self, message: str, stream: str = False):
        self._append_message(message=message, role="user")
        msg_cache = ""
        if stream == False:
            res = chat(model=self.model, messages=self.messages, stream=False)
            self._append_message(role="assistant", message=res["message"]["content"])
        else:
            """
            Should be removed
            """
            res = chat(model=self.model, messages=self.messages, stream=True)
            for chunk in res:
                msg_cache += chunk["message"]["content"]
                print(chunk["message"]["content"], end="", flush=True)
        return res["message"]["content"] if stream == False else msg_cache

    def completion_stream(self, message: str):
        self._append_message(message=message, role="user")
        res = chat(model=self.model, messages=self.messages, stream=True)
        for chunk in res:
            if chunk["message"]["content"]:
                yield chunk["message"]["content"]

    def get_client(self):
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required, but unused
        )
        return client

    def get_model(self):
        return self.model

    def get_llm_config(self) -> LLMConfig:
        return LLMConfig(provider="ollama/" + self.model, api_token=None)

    def clear_message(self):
        self.messages = []

    def _append_message(self, role: str, message: str):
        self.messages.append({"role": role, "content": message})
