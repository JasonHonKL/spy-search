from .agent import Agent
from ..prompt import planner_agent_prompt
from ..model import model

import json

from collections import deque


class Planner(Agent):
    def __init__(self, model: model, query: str):
        self.query = query
        self._model = model
        self._output_model = {}
        self._todo_list = _todo()

        self.message = [] 

    def run(self , task):
        """
        It should generate a to do list
        and then pass to different agent
        """

        # Initialization
        prompt = planner_agent_prompt(
            list(self._output_model.keys()),
            list(self._output_model.values()),
            self.query,
        )
        res = self._model.completion(prompt)
        json_response = self._extract_response(res)
        self._response_handler(json_response)

        # Main loop
        while self._todo_list.len() != 0:
            cur_task = self._todo_list.pop_task()
            agent = cur_task.agent
            task = cur_task.task
            # check if any information update from other agent
            res = agent.run(task)

    def add_model(self, model, description):
        self._output_model[model] = description

    def _response_handler(self, json_response):
        """
        For planner json response should be handling an array []
        add everything into the todo list queue
        """
        obj = json.loads(json_response)
        for response in obj:
            task = response["task"]
            agent = self._output_model[response["agent"]]
            self._todo_list.add_task(task, agent)


"""
    Private class to handle as a to do list
    One task --> multiple subtask to correct agent
"""


class _todo:
    def __init__(self):
        self.todo_list = deque()

    def add_task(self, task: str, Agent: Agent):
        self.todo_list.append(_task(task, Agent))

    def pop_task(self):
        return self.todo_list.popleft()

    def len(self):
        return len(self.todo_list)


class _task:
    def __init__(self, task: str, agent: Agent):
        self.task = task
        self.agent = agent
