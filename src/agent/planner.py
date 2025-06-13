from .agent import Agent
from ..prompt import planner_agent_prompt
from ..model import model

import json

from collections import deque

import logging

logger = logging.getLogger(__name__)


class Planner(Agent):
    def __init__(self, model: model, query: str = "", data=None):
        self.query = query
        self._model = model
        self._output_model = {}
        self._todo_list = _todo()

        self.message = []
        self.initialize = False

        self.response = ""
        self.db = []
        self.name = "planner"
        self.description = "plan the tasks"

    def get_recv_format(self):
        pass

    def get_send_format(self):
        pass

    def set_name(self, name):
        self.name = name

    async def run(self, response, data=[]):
        """
        It should generate a to do list
        and then pass to different agent
        """
        # Initialization
        # only run for oen time

        logger.info("planner running ... ...")
        if not self.initialize:
            prompt = planner_agent_prompt(
                list(self._output_model.keys()),
                list(self._output_model.values()),
                self.query,
            )
            res = self._model.completion(prompt)

            logger.info(f"get response {res}")

            self._response_todo_handler(res)

            self.initialize = True

            task = self._todo_list.pop_task()
            logger.info(f"handling {task.task}")

            obj = {"agent": task.agent, "task": task.task, "data": data}
            return obj
        else:
            self._response_handler(response)
            new_task = self._todo_list.pop_task()
            if new_task == None:
                logger.info("Terminate processs")
                obj = {"agent": "TERMINATE", "task": "TERMINATE", "data": data}
            else:
                obj = {"agent": new_task.agent, "task": new_task.task, "data": data}
                logger.info(f"handling next obj {obj}")
            return obj

    def _response_handler(self, response):
        pass

    def add_model(self, model, description):
        """
        Args:
            model: agent
            description: descripe the agent
        """
        self._output_model[model] = description

    def _response_todo_handler(self, json_response):
        """
        For planner json response should be handling an array []
        add everything into the todo list queue
        """
        obj = self._extract_response(json_response)
        logger.info(f"handling task {obj}")
        for response in obj:
            task = response["task"]
            agent = response["agent"]
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
        if self.len() == 0:
            return None
        return self.todo_list.popleft()

    def len(self):
        return len(self.todo_list)


class _task:
    def __init__(self, task: str, agent: Agent):
        self.task = task
        self.agent = agent
