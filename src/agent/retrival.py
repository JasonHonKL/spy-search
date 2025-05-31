from ..RAG.chrome import VectorSearch
from .agent import Agent
from ..prompt import retrival_agent_prompt

import json
import re


class RAG_agent(Agent):
    """
    RAG Agent should able to do search relevant content given a query
    It should also have it's own database for search relevant content and also chacing recent result
    Args:
        model: a LLM model
        path: db path , default "./db"
    """

    def __init__(self, model, path: str = "./db"):
        self.model = model
        self.db = VectorSearch(path=path)
        self.tool_list = ["Add_document", "Query", "Reset"]

    def run(self, task: str) -> str:
        self.task = task
        self.prompt = retrival_agent_prompt(self.tool_list, task=task)
        res = self.model.completion(self.prompt)
        json_res = self._extract_response(res)
        self._json_handler(json_res)
        return ""

    def _json_handler(self, res: str):
        """
        json handler handlers handle json response and then pass it to correct tool
        Args:
            res: the response should be a json string. If it is pure response it should pass to _extract_response first before
            passing to _json_handle
        """
        obj = json.loads(res)
        print(obj)
        print(obj["tool"])
        print(obj["args"])
