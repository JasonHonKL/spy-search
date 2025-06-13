from ..RAG.chrome import VectorSearch
from .agent import Agent
from ..model import Model
from ..prompt import retrieval_prompt
from ..utils import read_config

from markitdown import MarkItDown

import os
import string
import json

import logging

logger = logging.getLogger(__name__)


class RAG_agent(Agent):
    """
    RAG Agent should able to do search relevant content given a query
    It should also have it's own database for search relevant content and also chacing recent result
    Args:
        model: a LLM model
        path: db path , default "./db"
    """

    def __init__(
        self, model: Model, path: str = "./local_db", filelist="./local_files"
    ):
        logger.info("Initalize RAG agent")
        self.model = model
        self.db = VectorSearch(path=path)
        # TODO: maybe don't use hard reset ?
        self.db.reset()
        self.tool_list = ["add_document", "query", "reset"]

        config = read_config()
        self.filelist = config.get("db", filelist)

        self.name = "local-retrieval"
        self.description = "read local files and get summary"

    async def run(self, task: str, data: str) -> str:
        """
        one way work flow
        -- given a filelist
        read every documents from the file list
        -- do query
        use model to form {} format
        """
        logger.info("retrival running ...")
        mk = MarkItDown()
        for root, dirs, files in os.walk(self.filelist):
            for file in files:
                logger.info(f"handling the file{file}")
                self._file_handler(os.path.join(root, file), mk)

        result = self.db.query(task, 2)
        logger.info(f"get the result {result}")
        for i, docs in enumerate(result["documents"]):

            """
            TODO: refactor use localRAG class
            """
            file_path = result["metadatas"][0][i]["file"]  # fix: index correctly
            prompt = retrieval_prompt(docs, file_path)
            res = self.model.completion(prompt)
            logger.info(f"response from llm: {res}")
            res = self._extract_response(res)
            logger.info(f"getting response {res}")
            # res = json.loads(res)
            # logger.info(f"loading ... {res} ")
            data.append(res)

        return {"agent": "planner", "data": data, "task": ""}

    def _json_handler(self, res: str):
        """
        json handler handlers handle json response and then pass it to correct tool
        Args:
            res: the response should be a json string. If it is pure response it should pass to _extract_response first before
            passing to _json_handle
        """
        pass

    def get_recv_format(self):
        pass

    def get_send_format(self):
        pass

    def _todo(self, task):
        pass

    def _file_handler(self, filepath, mk: MarkItDown):
        result = mk.convert(filepath)
        result = result.markdown
        temp = ""
        for i, ch in enumerate(result):
            temp += ch
            if i % 1500 == 0 and i != 0:
                self.db.add_document(temp, str(i), {"file": filepath})

        self.db.add_document(temp, str(len(result) + 1), {"file": filepath})
