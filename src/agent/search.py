from .agent import Agent
from ..model import Model

from ..prompt.searcher import search_plan

from ..browser.crawl_ai import Crawl

from collections import deque
import json

import time 

import logging 
logger = logging.getLogger(__name__)

class Search_agent(Agent):
    def __init__(self, model:Model, k: int = 10):
        """
        take some default URL for search
        k: number of steps
        """
        self.model = model
        self.crawl = Crawl(model=model)
        self.description = "search latest information"

        self.search_web = [
            "https://google.com",
            "https://arxiv.com",
            "https://news.google.com",
            "https://scholar.google.com",
        ]

        self.todo = deque()
        self.step = 10
        self.url_list = []
        self.db = [] 
        self.name = "searcher"
    
    def set_name(self , name):
        self.name = name

    async def run(self, task, data) -> str:
        """
        Search function need to user the brower methods to search relevant contents
        - note that search agent should have it's own planner to plan search with what links

        Steps:
            1. Generate a to do list
            2. For each task
                read current short summary to plan the searching key word
                selecte the search_web
                allow one step depth search [hyper paramerter ?]
                script the content if irrelevant --> ignore
                if relevant --> self to db
                generate long short summary
            3. Return two things
                data: we want to reutrn the long summary
                for response we just need to response "FINISHED"
                AGENT: PLANNER
        """
        logger.info("SEARCHER: RUNNING ")
        logger.info(f"{self.todo} testing..")
        steps =self._plan(task)
        tools = {} 
        url_list = []
        cur_task = 0

        cur_db = [] 
        for d in data:
            cur_db.append(d["summary_list"])
        query = task[:]

        while cur_task < len(self.todo):
            new_task = self.todo[cur_task]
            logger.info(f"new task: {new_task}")
            tool , keyword , search_engine = new_task.get('tool', '') , new_task.get('keyword' , '') , new_task.get("search_engine" , "")

            match tool: 
                case "url_search":
                    urls = await self._search_url(keyword , cur_db , search_engine)
                    for url in urls:
                        self.url_list.append(url)
                case "page_content":
                    #logger.info(self.url_list)
                    await self._page_content(query)
                    self.url_list = [] 
                case _:
                    logger.info("TOOL NOT FOUND")
            cur_task +=1 

        return {"agent": "planner" , "data":self.db , "task":""}

    def get_send_format(self):
        pass

    def get_recv_format(self):
        pass

    def _plan(self , task:str , k:int=6):
        """
        Searcher planner
        """
        prompt = search_plan(task , self.todo , k)
        logger.info(f"task {task}")
        logger.info(prompt)

        response = self.model.completion(prompt)
        logger.info(f"searcher response: {response}")
        time.sleep(3) ## foo foo solution
        todo_list = (self._extract_response(response))
        
        logger.info(todo_list)
        k -= len(todo_list)
        for todo in todo_list:
            self.todo.append(todo)
        logger.info(f"self.todo in searcher: {self.todo}") 
        #logger.info(tasks)
        return k

    def _task_handler(self , task:str):
        pass

    async def _search_url(self , query, db , search_engine):
        """
            search url with google 
        """
        # test with google first
        # result is an array 
        #TODO update with duckduckgo

        logger.info("Search URL handling ... ")

        result = await self.crawl.get_url_llm("https://google.com/search?q="+query , query)
        return result

    async def _page_content(self, query):
        logger.info("page content handling ... ")
        if not self.url_list:
            return None # no url
        urls =[]
        for element in self.url_list:
            urls.append(element.get('url' , ""))
        summary_list = await self.crawl.get_summary(urls , query)

        for summary in summary_list:
            summary['url'] = summary.get('url', "")
            summary['title'] = summary.get('title', "")
            summary['summary'] = summary.get('summary', "")
            summary['brief_summary'] = summary.get('brief_summary', "")
            summary['keywords'] = summary.get('keywords', [])
            self.db.append(
                {
                    "title": summary['title'],
                    "brief_summary" : summary['brief_summary'],
                    "summary":summary['summary'],
                    "keywords":summary["keywords"],
                    "url": summary["url"],
                }
            )
        return summary_list
        
