# we may use crew_ai write some api for it
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMConfig,
)
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from markitdown import MarkItDown

import json
import requests
import os

from ..model import Model
from ..RAG.summary import Summary


class Crawl:
    """
    Crawl4ai should be used to support browser.py [Maybe we don't even need browser.py]
    with browser.py search some well known website for example google arxiv google scholar
    or some user self defined website --> seach all link

    --> then use crawl4ai to help for search

    All api is expected to be sync and use crawl4ai
    Expected API list
        get_links: given a url which is the result from a search website like google return the result list of that page
        get_images: get all images from the webpage
        get_content: get relevant content to a markdown


    we need to find a faster method
    """

    def __init__(self, model: Model, db=None, url_search=None):
        self.model = model
        self.crawler = AsyncWebCrawler()
        self.db = [] if db == None else db

        """
            The url_list is the list that we hope to search in the next ste 
            The url_search list is list of well known website that we want to search with 
        """
        self.url_list = []
        self.url_search = []

        self.broswer_conf = BrowserConfig()
        self.run_conf = CrawlerRunConfig()

    async def start_crawler(self):
        await self.crawler.start()

    async def close_crawler(self):
        await self.crawler.close()

    # problem: still so slow --> for example searching takes 124.12s for arxiv website
    # TODO: concurrent process other state first ?
    async def get_url_llm(self, url, query):
        """
        Get url from a website with the help of llm
        TODO: Replace Do Do Duck
        """
        self.broswer_conf = BrowserConfig(headless=True)
        self.run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=self.model.get_llm_config(),
                schema=Url_result.model_json_schema(),
                extraction_type="schema",
                instruction=f"""
                    You are given the content of a search results webpage. Your task is to extract the main URL, the title of the webpage, and a brief description of the webpage. 
                    You should give ALL linked that are relevant to the content {query} 

                    - The URL should be the full link to the webpage.
                    - The title should be the main heading or the title of the webpage.
                    - The description should be a concise summary or snippet describing the webpage content.
                    - Please return top 5 meaningful URL.

                    Return the result strictly in the JSON schema format as defined:

                    {{
                        "url": "string",
                        "description": "string",
                        "title": "string"
                    }}

                    Only provide the JSON object without additional text or explanation.
                    """,
            ),
        )
        self.crawler = AsyncWebCrawler(config=self.broswer_conf)
        await self.start_crawler()

        result = await self.crawler.arun(url=url, config=self.run_conf)
        await self.close_crawler()
        self.url_list = json.loads(result.extracted_content)

        return self.url_list

    async def get_pdf_summary(self, url):
        """
        download the pdf file
        user markitdown to convert to markdown
        generate summary with LLM --> we need a specific method to handle this
        """
        p = self._download_pdf(url)
        md = MarkItDown()
        result = md.convert(p)
        s = Summary(self.model)
        r = s.summary(result.markdown)
        del s
        return r

    async def get_summary(self, url: list, query):
        summary = []
        for u in url:
            is_pdf = await self._is_pdf(u)
            if is_pdf:
                try:
                    content = await self.get_pdf_summary(u)
                    response = await summary.append(content)
                    summary.append(response)
                except Exception as e:
                    print("Handling pdf error: ", e)
                # current not support pdf first
                url.remove(u)

        self.broswer_conf = BrowserConfig()
        self.run_conf = CrawlerRunConfig(
            word_count_threshold=1,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=self.model.get_llm_config(),
                schema=Page_summary.model_json_schema(),
                extraction_type="schema",
                instruction=f"""
                You are given the content of a webpage. Extract the following information relevant to the query: {query}

                - Title: The main title of the page.
                - Summary: A detailed summary describing the main content of the page. (around 300 - 400 words)
                - Brief_summary: A concise, one or two sentence summary of the page. (2 to 3 sentences)
                - Keywords: A list of relevant keywords or key phrases that represent the main topics of the page.
                - url: the page url

                Return the information as a JSON object matching this schema:

                {{
                    "title": "string",
                    "summary": "string",
                    "brief_summary": "string",
                    "keywords": ["string", "string", ...],
                    "url": "string,
                }}
                
                If the content is not relevant to the query, return:

                
                {{
                "title": "error",
                "summary": "error",
                "brief_summary": "error",
                "keywords": null, 
                "url": "",
                }}
            

                Only provide the JSON object without any additional text or explanation.
                """,
            ),
            cache_mode=CacheMode.BYPASS,
        )
        self.crawler = AsyncWebCrawler(config=self.broswer_conf)
        await self.start_crawler()

        result = await self.crawler.arun_many(
            urls=url,
            config=self.run_conf,
        )
        await self.close_crawler()

        for ele in result:
            page_summary = json.loads(ele.extracted_content)
            try:
                summary.append(page_summary[0])
            except:
                pass

        return summary

    async def get_table(self, url, query: str):
        """
        The performance of the get table is not good.  we may need to use VLLM to handle the table extraction job
        """
        self.browser_conf = BrowserConfig(headless=True)
        self.run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            page_timeout=5000,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=self.model.get_llm_config(),
                schema=TableData.model_json_schema(),
                extraction_type="schema",
                instruction=f"""
                    You are given the content of a webpage. Extract the main table on the page as a JSON object with the following structure:

                    - Include relevant information ONLY. Don't include html tag. I want clean data 
                    - Return ONLY the JSON object matching this schema, without any additional text or explanation.
                    - REMEMBER ONLY RELEVENT TO CONTENT TO THE QUERY SHOULD BE LISTED IN THE TABLE {query}
                    - IRRELEVANT CONTENT WILL BE CONSIDER RUBBISH AND SHOULD NOT BE INCLUDED

                    Extract the table content as plain text only. For each cell, include only the visible text, ignoring all HTML tags, attributes, images, and JavaScript.
                    Return the result strictly as JSON matching the schema.
                    THIS IS IMPORTANT "PLAIN TEXT" !

                    Example output:
                    {{
                    "rows": [
                        {{"cells": ["Header1", "Header2", "Header3"]}},
                        {{"cells": ["Row1Col1", "Row1Col2", "Row1Col3"]}},
                        {{"cells": ["Row2Col1", "Row2Col2", "Row2Col3"]}}
                    ]
                    }}
                """,
            ),
        )
        self.crawler = AsyncWebCrawler(config=self.browser_conf)
        await self.start_crawler()

        result = await self.crawler.arun(url=url, config=self.run_conf)
        await self.close_crawler()

        # Parse the JSON extracted content into TableData model

        return result

    async def screen_shot(self, url):
        self.broswer_conf = BrowserConfig(headless=False, verbose=True)
        self.run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            screenshot=True,
            scan_full_page=True,
            wait_for_images=True,
        )

        self.crawler = AsyncWebCrawler(config=self.broswer_conf)
        await self.start_crawler()

        result = await self.crawler.arun(url=url, config=self.run_conf)

        if result.screenshot:
            from base64 import b64decode

            with open("./tmp/screenshot/screenshot.png", "wb") as f:
                f.write(b64decode(result.screenshot))

        await self.close_crawler()

    async def _is_pdf(self, url):
        try:
            # Use GET request with stream=True to avoid downloading the entire file
            response = requests.get(url, stream=True, allow_redirects=True, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()
            # Check if content-type indicates PDF
            if "application/pdf" in content_type:
                return True

            # Sometimes content-type is not set correctly,
            # so check the first 5 bytes for '%PDF-'
            start = response.raw.read(5)
            return start == b"%PDF-"

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return False

    def search_content(self):
        pass

    def run(self):
        pass

    def _download_pdf(self, url, save_path="./tmp"):
        """
        Download every file ?
        """
        filename = url.rstrip("/").split("/")[-1]
        filename = filename.split("?")[0]
        # Ensure the filename ends with .pdf
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        save_path = os.path.join(save_path, filename)

        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path


class Url_result(BaseModel):
    url: str = Field(..., description="the link")
    description: str = Field(..., description="description of the website")
    title: str = Field(..., description="title of the webpage")


class Page_summary(BaseModel):
    title: str = Field(..., description="Title of the page.")
    summary: str = Field(..., description="Summary of the page")
    brief_summary: str = Field(..., description="Brief summary of the page")
    keywords: list[str] = Field(..., description="Keywords assigned to the page")


class TableRow(BaseModel):
    cells: list[str] = Field(..., description="List of cell values in the row")


class TableData(BaseModel):
    rows: list[TableRow] = Field(..., description="List of rows in the table")
