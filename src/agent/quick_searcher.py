from ..browser import DuckSearch
from .agent import Agent


class Quick_searcher(Agent):
    """
    Instead of search so slow use do do duck searcher to search faster
    """

    def __init__(self, model):
        self.model = model
        self.searcher = DuckSearch()

        self.name = "quick-searcher"
        self.description = "search latest information with high speed"

    def get_recv_format(self):
        pass

    def get_send_format(self):
        pass

    def set_name(self, name):
        self.name = name

    async def run(self, query, data=[]):
        """
        quick search use do do duck to do quick search and response
        different from the quick search response it return data and
        act as an agent

        maybe selecte relevant web ?
        """
        res = self.searcher.search_result(query)
        for ele in res:
            result = {
                "title": ele["title"],
                "summary": ele.get("full_content", ""),
                "brief_summary": ele["snippet"],
                "keywords": [],
                "url": ele["link"],
            }
            data.append(result)
        return {"agent": "planner", "data": data, "task": ""}
