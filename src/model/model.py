from abc import ABC, abstractmethod

from crawl4ai import LLMConfig


class Model(ABC):
    """
    This is an abstraction class for models
    Model can be any LLM or VLM

    TODO: should we have one api that support
    """

    @abstractmethod
    def __init__(self):
        pass

    """
        Completion is 
        Args:
            query: query can be a prompt or RAG sentence
        Output:
            return a string response
    """

    @abstractmethod
    def completion(self, query: str) -> str:
        pass

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def get_llm_config(self) -> LLMConfig:
        pass

    @abstractmethod
    def set_api(self, api: str) -> None:
        pass

    @abstractmethod
    def clear_message(self):
        pass

    @abstractmethod
    def completion_stream(self, message):
        pass
