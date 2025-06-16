from .agent import Agent
from ..prompt.reporter import report_prompt, report_plan, report_task

from ..model import Model

import string
import secrets
import json

import time

import logging

logger = logging.getLogger(__name__)


class Reporter(Agent):
    def __init__(self, model: Model):
        self.model: Model = model
        self.todo = []
        self.db = None

        self.description = "generateing report"

        self.source = {}
        self.name = "reporter"

        self.length = 4  # the length of uuid

    def set_name(self, name):
        self.name = name

    async def run(self, query: str, data=None):
        """
        based on query and data to write a response
        Maybe we plan what to write and write a report style ?
        """
        self.db = self.data_handler(data=data)
        short_summary = self.data_handler(data)

        logger.info(f"short summary {short_summary}")

        res = await self._planner(query=query, db=short_summary)

        logger.info(f"reporter response {res}")

        # problem it is not yet response and then it return and the problem is it can't extract correct res afterward
        tasks = self._extract_response(res)
        # tasks = json.loads(tasks)

        logger.info(f"handling tasks {tasks}")

        r = self._task_handler(tasks)

        logger.info(f"response {r}")

        return {"agent": "TERMINATE", "data": r, "task": ""}

    def data_handler(self, data):
        if not isinstance(data, list):
            print("error handling data")
            return

        short_summaries = []
        alphabet = string.ascii_letters + string.digits

        # Store processed items with IDs for future referencing
        processed_data = []

        for d in data:
            rand_id = "".join(secrets.choice(alphabet) for _ in range(self.length))

            col = {
                "id": rand_id,
                "url": d.get("url", ""),
                "title": d.get("title", ""),
                "summary": d.get("summary", ""),
                "brief_summary": d.get("brief_summary", ""),
                "keywords": d.get("keywords", []),
            }
            processed_data.append(col)

            if col["summary"] != "":
                short_summaries.append({"id": rand_id, "short_summary": col["summary"]})
        self.source = processed_data
        return short_summaries

    # Suppose you got a short summary id and want to get the long summary
    def get_source(self, summary_ids: list[int]) -> list[object]:
        sources = []
        for item in self.source:
            if item["id"] in summary_ids:
                sources.append(item)
        return sources

    def get_recv_format(self):
        pass

    def get_send_format(self):
        pass

    async def _planner(self, query, db=None):
        print("planning what to write")
        prompt = report_plan(query, db)
        res = self.model.completion(prompt)
        return res

    def _task_handler(self, tasks):
        i = 0
        final_report = ""
        for task in tasks:
            t = task.get("task", "")
            data = task.get("data", "")

            logger.info(f"handling task {t}")

            source = self.get_source(data)

            logger.info(f"reading sources ... {source}")

            prompt = report_task(tasks, t, source)
            res = self.model.completion(prompt)
            logger.info(f"geting response {res}")
            res = self._extract_response(res)

            logger.info(f"getting response {res}")
            try:
                final_report += "\n"
                final_report += res["content"]
                logger.info(res)
                logger.info(type(res))
            except:
                final_report += ""
            logger.info("final report ... ")  # maybe yield final report here ?

        return final_report

    def _get_relevant_data(self):
        pass
