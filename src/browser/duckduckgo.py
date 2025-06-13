import re
import requests
from html import unescape
from langchain_community.tools import DuckDuckGoSearchResults
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

import time

import logging

logger = logging.getLogger(__name__)


class DuckSearch:
    def __init__(self):
        self.search_engine = DuckDuckGoSearchResults(
            backend="text", output_format="list"
        )
        self.news_engine = DuckDuckGoSearchResults(
            backend="news", output_format="list", num_results=9
        )

    def _extract_full_text(self, url: str, limit: int = 400) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()  # Raise HTTPError if bad response

            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")

            # Extract text, unescape HTML entities, strip whitespace
            texts = [
                unescape(p.get_text(strip=True))
                for p in paragraphs
                if p.get_text(strip=True)
            ]

            text = " ".join(texts)
            logger.info(text)
            return text[:limit].strip()

        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch {url} -> {e}")
            return ""

    def search_result(
        self, query: str, k: int = 5, backend: str = "text", deep_search: bool = True
    ) -> list:
        logger.info("start searching... ")
        results = self.search_engine.invoke(query)
        if deep_search:

            def _extract_and_update(result):
                url = result.get("link")
                full_text = self._extract_full_text(url)
                result["full_content"] = full_text
                return result

            with ThreadPoolExecutor(max_workers=k) as executor:
                futures = [
                    executor.submit(_extract_and_update, result)
                    for result in results[:k]
                ]
                done, not_done = wait(futures, timeout=4)
                for future in not_done:
                    future.cancel()
                for future in done:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[ERROR] Exception during deep search extraction: {e}")
        logger.info("end searching ...")
        return results[:k]

    def today_new(self, category: str) -> list:
        if category == "technology":
            category_query = "latest technology and science news"
        elif category == "finance":
            category_query = "latest finance news"
        elif category == "entertainment":
            category_query = "latest entertainment and culture news"
        elif category == "sports":
            category_query = "latest sports news"
        elif category == "world":
            category_query = "latest world news"
        elif category == "health":
            category_query = "latest health and healthcare news"
        else:
            category_query = "latest news"
        return self.news_engine.invoke(category_query)
