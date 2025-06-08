"""
Factory
"""

from ..agent import Planner, Search_agent, Reporter, RAG_agent
from ..agent.notion import NotionAgent
from ..model import Gemini, Ollama, Deepseek, Model, Gork, OpenAI


class Factory:
    def get_agent(agent_name: str, model: Model):
        if agent_name == "planner":
            return Planner(model)
        elif agent_name == "reporter":
            return Reporter(model)
        elif agent_name == "searcher":
            return Search_agent(model)
        elif agent_name == "notion":
            return NotionAgent(model)
        elif agent_name == "local-retrieval":
            return RAG_agent(model)

    def get_model(provider: str, model: str) -> Model:
        if provider == "deepseek":
            return Deepseek(model)
        if provider == "google" or provider == "gemini":
            return Gemini(model)
        if provider == "ollama" or provider == "ollama":
            return Ollama(model)
        if provider == "xAI" or provider == "gork":
            return Gork(model)
        if provider == "openai" or provider == "gpt":
            return OpenAI(model)

        return None
