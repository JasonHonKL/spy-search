import asyncio
import aiohttp
from html import unescape
from langchain_community.tools import DuckDuckGoSearchResults
import logging
from typing import List, Dict, Optional, Set, Tuple
import time
from functools import lru_cache
import re
from urllib.parse import urlparse
import threading
import concurrent.futures
from collections import deque # Kept for general utility, but _session_pool is removed
import gc
from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)

class DuckSearch:
    def __init__(self):
        self.search_engine = DuckDuckGoSearchResults(
            backend="text", output_format="list"
        )
        self.news_engine = DuckDuckGoSearchResults(
            backend="news", output_format="list", num_results=8
        )
        
        self._connector_config = {
            'limit': 300,
            'limit_per_host': 100,
            'ttl_dns_cache': 3600,
            'use_dns_cache': True,
            'keepalive_timeout': 120,
            'enable_cleanup_closed': True,
            'force_close': False,
            'ssl': False,
        }
        
        self._timeout_config = aiohttp.ClientTimeout(
            total=0.8,
            connect=0.2,
            sock_read=0.6
        )

        # threading.local() will store a unique TCPConnector instance per thread
        self._thread_local_connector = threading.local() 

        # Removed: self._session_pool and self._session_lock
        # Sessions will now be managed per deep search/warmup execution.

        self._failed_urls: Set[str] = set()
        self._content_cache: Dict[str, str] = {}
        self._url_cache: Dict[str, bool] = {}
        
        self._text_cleanup = re.compile(r'\s+')
        self._html_tags = re.compile(r'<[^>]+>')
        self._extract_paragraphs = re.compile(r'<p[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL)
        
        self._warmup_done = False
        self._background_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="bg-duck"
        )
        self._sync_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="sync-async-bridge"
        )

        self._start_background_warmup()

    def _start_background_warmup(self):
        """Submits a warmup task to the background executor."""
        def warmup_task_wrapper():
            # This function runs in a new thread.
            # asyncio.run handles loop creation, setting, running, and closing.
            try:
                # _warmup_sessions will now create and close its own thread-local connector and session
                asyncio.run(self._warmup_sessions())
            except Exception as e:
                logger.debug(f"Warmup task error: {e}")
            finally:
                # Cleanup thread-local storage key for the connector (it should already be closed)
                if hasattr(self._thread_local_connector, 'conn'):
                    del self._thread_local_connector.conn
                    logger.debug(f"Cleaned up thread-local connector storage in background warmup thread {threading.current_thread().name}")
        
        self._background_executor.submit(warmup_task_wrapper)

    async def _warmup_sessions(self):
        """Pre-create optimized sessions. Runs in an asyncio loop in a worker thread."""
        # This must be the first thing to happen within this async function,
        # ensuring the connector is created within the active event loop of THIS thread.
        if not hasattr(self._thread_local_connector, 'conn') or self._thread_local_connector.conn.closed:
            self._thread_local_connector.conn = aiohttp.TCPConnector(**self._connector_config)
            logger.debug(f"Created new TCPConnector for thread {threading.current_thread().name} (warmup)")

        session: Optional[aiohttp.ClientSession] = None
        try:
            session = await self._create_optimized_session() # Create a session for this warmup task
            
            # Perform a few dummy requests to warm up the connections
            # Using try-except for dummy requests to not fail the whole warmup on one issue
            dummy_urls = ["http://example.com", "http://google.com"]
            for url in dummy_urls:
                try:
                    async with session.get(url, timeout=0.5) as resp:
                        await resp.read() # Read content to ensure connection is fully used
                        logger.debug(f"Warmup successful for {url} with status {resp.status}")
                except (asyncio.TimeoutError, aiohttp.ClientError, Exception) as e:
                    logger.debug(f"Warmup failed for {url}: {e}")

            self._warmup_done = True
            logger.debug(f"Warmed up connections in background thread {threading.current_thread().name}.")
        finally:
            # Ensure the session and thread-local connector are closed
            if session and not session.closed:
                await session.close()
                logger.debug(f"Closed warmup ClientSession in thread {threading.current_thread().name}")
            if hasattr(self._thread_local_connector, 'conn') and not self._thread_local_connector.conn.closed:
                await self._thread_local_connector.conn.close()
                logger.debug(f"Closed TCPConnector in warmup task for thread {threading.current_thread().name}")

    async def _create_optimized_session(self) -> aiohttp.ClientSession:
        """Creates and returns a new aiohttp.ClientSession instance.
        It assumes _thread_local_connector.conn has been initialized by the calling async context."""
        
        if not hasattr(self._thread_local_connector, 'conn') or self._thread_local_connector.conn.closed:
            logger.error("Thread-local TCPConnector not found or closed. Re-creating for safety. (This indicates an unexpected state)")
            self._thread_local_connector.conn = aiohttp.TCPConnector(**self._connector_config)
            
        session = aiohttp.ClientSession(
            connector=self._thread_local_connector.conn,
            timeout=self._timeout_config,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "text/html,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "DNT": "1",
            },
            read_bufsize=32768,
            skip_auto_headers={"User-Agent"},
            connector_owner=False, # DuckSearch (or the thread's lifecycle) is responsible for closing the connector
        )
        return session

    # Removed _get_session_fast as sessions are now passed explicitly or created per context

    @lru_cache(maxsize=2000)
    def _is_valid_url_cached(self, url: str) -> bool:
        """Cached URL validation using urlparse."""
        if url in self._url_cache:
            return self._url_cache[url]
        
        try:
            parsed = urlparse(url)
            is_valid = bool(parsed.netloc and parsed.scheme in ('http', 'https'))
            self._url_cache[url] = is_valid
            return is_valid
        except:
            self._url_cache[url] = False
            return False

    async def _extract_content_blazing(self, session: aiohttp.ClientSession, url: str, limit: int = 300) -> str:
        """Blazing fast content extraction with all optimizations."""
        if not url or url in self._failed_urls:
            return ""
        
        if url in self._content_cache:
            return self._content_cache[url]
            
        if not self._is_valid_url_cached(url):
            self._failed_urls.add(url)
            return ""
        
        try:
            async with session.get(url, allow_redirects=False) as response:
                if response.status not in (200, 301, 302):
                    self._failed_urls.add(url)
                    logger.debug(f"Failed status for {url}: {response.status}")
                    return ""
                
                if response.status in (301, 302):
                    redirect_url = response.headers.get('Location')
                    if redirect_url and len(redirect_url) < 200:
                        logger.debug(f"Redirecting {url} to {redirect_url}")
                        return await self._extract_content_blazing(session, redirect_url, limit) # Pass session recursively
                    else:
                        self._failed_urls.add(url)
                        return ""
                
                content_bytes = b""
                async for chunk in response.content.iter_chunked(16384):
                    content_bytes += chunk
                    if len(content_bytes) > 40000:
                        break
            
            content_str = content_bytes.decode('utf-8', errors='replace') 
            
            texts = []
            full_text_so_far = ""

            try:
                tree = HTMLParser(content_str)
                paragraphs = tree.css('p')
                
                for i, node in enumerate(paragraphs):
                    if i >= 25:
                        break
                    text = node.text(strip=True)
                    if text and len(text) > 20:
                        texts.append(text)
                        full_text_so_far = " ".join(texts)
                        if len(full_text_so_far) > limit * 1.2:
                            break
                            
            except Exception as e:
                logger.debug(f"Selectolax failed for {url}: {e}. Falling back to regex.")
                matches = self._extract_paragraphs.findall(content_str)
                texts = []
                for match in matches[:25]:
                    text = self._html_tags.sub('', match).strip()
                    if text and len(text) > 20:
                        texts.append(text)
                        full_text_so_far = " ".join(texts)
                        if len(full_text_so_far) > limit * 1.2:
                            break
            
            if not texts:
                self._failed_urls.add(url)
                return ""
            
            final_text = self._text_cleanup.sub(' ', unescape(full_text_so_far)).strip()
            final_text = final_text[:limit]
            
            if len(self._content_cache) > 500:
                old_keys = list(self._content_cache.keys())[:100]
                for key in old_keys:
                    del self._content_cache[key]
            
            self._content_cache[url] = final_text
            return final_text

        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            self._failed_urls.add(url)
            logger.debug(f"Client error/timeout for {url}: {e}")
            return ""
        except Exception as e:
            self._failed_urls.add(url)
            logger.error(f"Unexpected error extracting content from {url}: {e}")
            return ""

    async def _process_result_blazing(self, session: aiohttp.ClientSession, result: Dict) -> Dict:
        """Lightning result processing - adds full_content to a search result."""
        url = result.get("link")
        if not url or url in self._failed_urls:
            result["full_content"] = ""
            return result
            
        content = await self._extract_content_blazing(session, url) # Pass session
        result["full_content"] = content
        return result

    async def _deep_search_blazing(self, results: List[Dict], k: int) -> List[Dict]:
        """Blazing fast deep search with maximum concurrency.
        Runs in an asyncio loop in a worker thread, creates its own session."""
        # Ensure a TCPConnector instance exists and is open for the CURRENT thread's event loop.
        if not hasattr(self._thread_local_connector, 'conn') or self._thread_local_connector.conn.closed:
            self._thread_local_connector.conn = aiohttp.TCPConnector(**self._connector_config)
            logger.debug(f"Created new TCPConnector for thread {threading.current_thread().name} (deep search)")

        session: Optional[aiohttp.ClientSession] = None
        try:
            session = await self._create_optimized_session() # Create a dedicated session for this deep search run
            
            if not results:
                return []
            
            max_concurrent = min(k * 8, 200)
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(result_item):
                async with semaphore:
                    # Pass the session down to the processing function
                    return await self._process_result_blazing(session, result_item)
            
            tasks = []
            initial_results_copy = results[:k] 
            
            for result in initial_results_copy:
                url = result.get("link", "")
                if url and url not in self._failed_urls and self._is_valid_url_cached(url):
                    task = asyncio.create_task(process_with_semaphore(result))
                    tasks.append(task)
                else:
                    result["full_content"] = ""
                    dummy_task = asyncio.create_task(asyncio.sleep(0)) 
                    dummy_task.set_result(result)
                    tasks.append(dummy_task)
            
            if not tasks:
                return initial_results_copy
            
            start_time = time.time()
            completed_results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=0.9
            )
            
            processing_time = time.time() - start_time
            logger.debug(f"Blazing deep search completed in {processing_time:.3f}s for {len(completed_results)} results.")
            
            final_results = []
            for i, result_or_exc in enumerate(completed_results):
                if isinstance(result_or_exc, Exception):
                    original_result = initial_results_copy[i] 
                    original_result["full_content"] = ""
                    final_results.append(original_result)
                    logger.debug(f"Task for {original_result.get('link')} failed: {result_or_exc}")
                else:
                    final_results.append(result_or_exc)
            
            return final_results[:k]
            
        except asyncio.TimeoutError:
            cancelled_count = 0
            for task in tasks:
                if not task.done():
                    task.cancel()
                    cancelled_count += 1
            
            logger.debug(f"Deep search Timeout - cancelled {cancelled_count} tasks.")
            
            partial_results = []
            for i, task in enumerate(tasks):
                if task.done():
                    try:
                        result = task.result()
                        if isinstance(result, Exception):
                             original_result = initial_results_copy[i]
                             original_result["full_content"] = ""
                             partial_results.append(original_result)
                        else:
                            partial_results.append(result)
                    except asyncio.CancelledError:
                        original_result = initial_results_copy[i]
                        original_result["full_content"] = ""
                        partial_results.append(original_result)
                    except Exception as e:
                        original_result = initial_results_copy[i]
                        original_result["full_content"] = ""
                        partial_results.append(original_result)
                else:
                    original_result = initial_results_copy[i]
                    original_result["full_content"] = ""
                    partial_results.append(original_result)
            return partial_results[:k]
        except Exception as e:
            logger.error(f"Unexpected error in _deep_search_blazing: {e}")
            for result in initial_results_copy:
                result["full_content"] = ""
            return initial_results_copy[:k]
        finally:
            # Ensure the session and thread-local connector are closed within the same event loop they were created.
            if session and not session.closed:
                await session.close()
                logger.debug(f"Closed deep search ClientSession in thread {threading.current_thread().name}")
            if hasattr(self._thread_local_connector, 'conn') and not self._thread_local_connector.conn.closed:
                await self._thread_local_connector.conn.close()
                logger.debug(f"Closed TCPConnector in deep search for thread {threading.current_thread().name}")


    def search_result(
        self, query: str, k: int = 6, backend: str = "text", deep_search: bool = True
    ) -> List[Dict]:
        """Blazing fast search with maximum performance.
        This method handles bridging sync calls to async operations efficiently."""
        start_time = time.time()
        logger.info(f"Starting blazing search for query: '{query}'")
        
        try:
            results = self.search_engine.invoke(query , max_results=4)
            logger.info(results)
            if not results:
                logger.info(f"No initial results found for query: '{query}'.")
                return []
        except Exception as e:
            logger.error(f"DuckDuckGo search invocation error: {e}")
            return []
        
        if not deep_search:
            search_time = time.time() - start_time
            logger.info(f"⚡ Basic search complete: {search_time:.3f}s")
            return results[:k]
        
        logger.info(f"Initiating deep processing for {len(results)} initial results...")
        
        try:
            def _run_deep_search_isolated_wrapper():
                # This function runs in a separate thread managed by _sync_executor.
                # asyncio.run handles loop creation, setting, running, and closing.
                # _deep_search_blazing will create and close its own thread-local connector and session.
                return asyncio.run(self._deep_search_blazing(results, k))

            future = self._sync_executor.submit(_run_deep_search_isolated_wrapper)
            final_results = future.result(timeout=2.5) # This timeout protects the calling thread

            search_time = time.time() - start_time
            logger.info(f"🚀 Blazing deep search complete: {search_time:.3f}s")
            return final_results
                
        except concurrent.futures.TimeoutError:
            logger.error(f"Deep search thread timed out after 2.5s for query: '{query}'. Returning partial results.")
            for res in results[:k]:
                if "full_content" not in res:
                    res["full_content"] = ""
            return results[:k]
        except Exception as e:
            logger.error(f"Blazing deep search error for query '{query}': {e}. Returning initial results.")
            for res in results[:k]:
                res["full_content"] = ""
            return results[:k]


    def today_new(self, category: str) -> List[Dict]:
        """Lightning news retrieval."""
        category_queries = {
            "technology": "latest tech science AI news",
            "finance": "latest finance market news", 
            "entertainment": "latest entertainment culture news",
            "sports": "latest sports news",
            "world": "latest world breaking news",
            "health": "latest health medical news"
        }
        
        query = category_queries.get(category, "latest breaking news")
        try:
            return self.news_engine.invoke(query)
        except Exception as e:
            logger.error(f"News search error for category '{category}': {e}")
            return []

    def clear_cache(self):
        """Aggressive cache clearing."""
        logger.info("Clearing all internal caches.")
        self._content_cache.clear()
        self._failed_urls.clear()
        self._url_cache.clear()
        self._is_valid_url_cached.cache_clear()
        gc.collect()

    async def cleanup(self):
        """Ultra-fast asynchronous cleanup of resources."""
        logger.info("Starting DuckSearch cleanup...")
        
        # All session and connector cleanup is handled within the async functions
        # (_warmup_sessions, _deep_search_blazing) and their finally blocks.
        # We just need to ensure the executors themselves shut down gracefully.
        
        self.clear_cache()
        
        if self._background_executor:
            # wait=True ensures tasks complete, allowing their finally blocks to run.
            self._background_executor.shutdown(wait=True, cancel_futures=True) 
            logger.debug("Background executor shutdown complete.")
        if self._sync_executor:
            self._sync_executor.shutdown(wait=True, cancel_futures=True)
            logger.debug("Sync executor shutdown complete.")
        
        logger.info("DuckSearch cleanup complete.")

    def __del__(self):
        """Fast cleanup on object deletion - best effort, as async cleanup is preferred."""
        try:
            # Initiate shutdown for executors, but don't wait in __del__ as it can block.
            if hasattr(self, '_background_executor') and self._background_executor:
                self._background_executor.shutdown(wait=False)
            if hasattr(self, '_sync_executor') and self._sync_executor:
                self._sync_executor.shutdown(wait=False)
            
            # Note: No session/connector closing here anymore. This is handled by the async methods.
        except Exception as e:
            logger.debug(f"Error during __del__ cleanup: {e}")