from abc import ABC, abstractmethod

import re
import json
import ast

from pydantic import BaseModel

"""
    This is an abstract class for Agent
    Here we will list out method that an Agent should have 
"""


class Agent(ABC):

    def __init__(self, model):
        self.model = model
        self.name: str
        self.description: str

    """
        An agent should have a run method such that it can run it's workflow 
        NOTE: choosing right tool for the right job should also place in the run method
    """

    @abstractmethod
    async def run(self, response, data=None):
        pass

    @abstractmethod
    def get_recv_format(self) -> BaseModel:
        pass

    @abstractmethod
    def get_send_format(self) -> BaseModel:
        pass

    def _extract_response(self, res: str):
        """
        Extract JSON or Python literal from a string that may contain markdown code blocks or plain text.
        Handles both JSON (double quotes) and Python literals (single quotes).
        Returns a Python dict or list (parsed), or None if no valid data found.
        """
        # Extract markdown code blocks first
        markdown_pattern = r"```(?:json\s*)?\n?(.*?)\n?```"
        markdown_matches = re.findall(markdown_pattern, res, re.DOTALL)

        for match in markdown_matches:
            match = match.strip()
            if match.startswith(("{", "[")):
                try:
                    parsed = json.loads(match)
                    return parsed
                except json.JSONDecodeError:
                    try:
                        parsed = ast.literal_eval(match)
                        return parsed
                    except Exception:
                        continue

        # Find JSON or Python literals in plain string
        json_candidates = []
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = 0
            while True:
                start_pos = res.find(start_char, start_idx)
                if start_pos == -1:
                    break
                bracket_count = 0
                end_pos = start_pos
                for i in range(start_pos, len(res)):
                    char = res[i]
                    if char == start_char:
                        bracket_count += 1
                    elif char == end_char:
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i
                            break
                if bracket_count == 0:
                    candidate = res[start_pos : end_pos + 1].strip()
                    json_candidates.append(candidate)
                start_idx = start_pos + 1

        valid_candidates = []
        for candidate in json_candidates:
            try:
                parsed = json.loads(candidate)
                valid_candidates.append((candidate, parsed))
            except json.JSONDecodeError:
                try:
                    parsed = ast.literal_eval(candidate)
                    valid_candidates.append((candidate, parsed))
                except Exception:
                    continue

        if valid_candidates:
            largest = max(valid_candidates, key=lambda x: len(x[0]))
            return largest[1]

        return None
