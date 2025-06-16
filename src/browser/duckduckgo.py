import asyncio
import aiohttp
import os
import json
from html import unescape
from langchain_community.tools import DuckDuckGoSearchResults
import logging
from typing import List, Dict, Optional, Set, Tuple, Literal
import time
from functools import lru_cache
import re
from urllib.parse import urlparse
import threading
import concurrent.futures
import gc
from selectolax.parser import HTMLParser

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading .env file
    pass

logger = logging.getLogger(__name__)

SearchBackend = Literal["duckduckgo", "serper", "auto"]

class SearchConfig:
    """Configuration class for search parameters"""
    def __init__(self):
        self.connector_config = {
            'limit': 300,
            'limit_per_host': 100,
            'ttl_dns_cache': 3600,
            'use_dns_cache': True,
            'keepalive_timeout': 120,
            'enable_cleanup_closed': True,
            'force_close': False,
            'ssl': False,
        }
        
        self.timeout_config = aiohttp.ClientTimeout(
            total=0.8,
            connect=0.2,
            sock_read=0.6
        )
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "text/html,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
        }
        
        self.max_content_length = 40000
        self.chunk_size = 16384
        self.read_buffer_size = 32768
        self.max_paragraphs = 25

class ContentExtractor:
    """Handles content extraction from web pages"""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self._text_cleanup = re.compile(r'\s+')
        self._html_tags = re.compile(r'<[^>]+>')
        self._extract_paragraphs = re.compile(r'<p[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL)
    
    async def extract_content(self, session: aiohttp.ClientSession, url: str, limit: int = 300) -> str:
        """Extract content from a URL with optimized parsing"""
        try:
            async with session.get(url, allow_redirects=False) as response:
                if response.status not in (200, 301, 302):
                    logger.debug(f"Failed status for {url}: {response.status}")
                    return ""
                
                if response.status in (301, 302):
                    redirect_url = response.headers.get('Location')
                    if redirect_url and len(redirect_url) < 200:
                        logger.debug(f"Redirecting {url} to {redirect_url}")
                        return await self.extract_content(session, redirect_url, limit)
                    else:
                        return ""
                
                content_bytes = await self._read_content_chunks(response)
                content_str = content_bytes.decode('utf-8', errors='replace')
                
                return self._parse_content(content_str, limit)
                
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            logger.debug(f"Client error/timeout for {url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error extracting content from {url}: {e}")
            return ""
    
    async def _read_content_chunks(self, response) -> bytes:
        """Read response content in chunks"""
        content_bytes = b""
        async for chunk in response.content.iter_chunked(self.config.chunk_size):
            content_bytes += chunk
            if len(content_bytes) > self.config.max_content_length:
                break
        return content_bytes
    
    def _parse_content(self, content_str: str, limit: int) -> str:
        """Parse HTML content and extract meaningful text"""
        texts = []
        full_text_so_far = ""

        try:
            # Primary parsing with selectolax
            tree = HTMLParser(content_str)
            paragraphs = tree.css('p')
            
            for i, node in enumerate(paragraphs):
                if i >= self.config.max_paragraphs:
                    break
                text = node.text(strip=True)
                if text and len(text) > 20:
                    texts.append(text)
                    full_text_so_far = " ".join(texts)
                    if len(full_text_so_far) > limit * 1.2:
                        break
                        
        except Exception as e:
            logger.debug(f"Selectolax parsing failed: {e}. Falling back to regex.")
            # Fallback to regex parsing
            matches = self._extract_paragraphs.findall(content_str)
            texts = []
            for match in matches[:self.config.max_paragraphs]:
                text = self._html_tags.sub('', match).strip()
                if text and len(text) > 20:
                    texts.append(text)
                    full_text_so_far = " ".join(texts)
                    if len(full_text_so_far) > limit * 1.2:
                        break
        
        if not texts:
            return ""
        
        final_text = self._text_cleanup.sub(' ', unescape(full_text_so_far)).strip()
        return final_text[:limit]

class SerperSearchEngine:
    """SERPER API integration for search functionality"""
    
    def __init__(self):
        # Try to load SERPER_API_KEY from environment (including .env file)
        self.api_key = os.getenv('SERPER_API_KEY')
        if self.api_key:
            logger.info("SERPER API key loaded successfully")
        else:
            logger.debug("SERPER_API_KEY not found in environment variables")
        
        self.base_url = "https://google.serper.dev"
        
    def is_available(self) -> bool:
        """Check if SERPER API key is available"""
        return bool(self.api_key)
    
    async def search(self, session: aiohttp.ClientSession, query: str, num_results: int = 10, search_type: str = "search") -> List[Dict]:
        """Perform search using SERPER API"""
        if not self.is_available():
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        url = f"{self.base_url}/{search_type}"
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': min(num_results, 100)  # SERPER API limit
        }
        
        try:
            # Use longer timeout for SERPER API
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                if response.status != 200:
                    response_text = await response.text()
                    logger.error(f"SERPER API error: {response.status} - {response_text}")
                    return []
                
                data = await response.json()
                logger.debug(f"SERPER API response: {data}")
                return self._parse_serper_results(data, search_type)
                
        except asyncio.TimeoutError:
            logger.error(f"SERPER API timeout for query: {query}")
            return []
        except aiohttp.ClientError as e:
            logger.error(f"SERPER API client error: {e}")
            return []
        except Exception as e:
            logger.error(f"SERPER API request failed: {e}")
            return []
    
    def _parse_serper_results(self, data: Dict, search_type: str) -> List[Dict]:
        """Parse SERPER API response to standard format"""
        results = []
        
        if search_type == "search":
            # Handle organic results
            if "organic" in data:
                for item in data["organic"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
            # Handle knowledge graph results
            elif "knowledgeGraph" in data:
                kg = data["knowledgeGraph"]
                results.append({
                    "title": kg.get("title", ""),
                    "link": kg.get("website", ""),
                    "snippet": kg.get("description", "")
                })
            # Handle answer box
            elif "answerBox" in data:
                ab = data["answerBox"]
                results.append({
                    "title": ab.get("title", ""),
                    "link": ab.get("link", ""),
                    "snippet": ab.get("snippet", ab.get("answer", ""))
                })
                
        elif search_type == "news":
            if "news" in data:
                for item in data["news"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "date": item.get("date", "")
                    })
        
        logger.debug(f"Parsed {len(results)} results from SERPER API")
        return results

class SessionManager:
    """Manages aiohttp sessions and connectors per thread"""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self._thread_local_connector = threading.local()
    
    def get_connector(self) -> aiohttp.TCPConnector:
        """Get or create thread-local connector"""
        if not hasattr(self._thread_local_connector, 'conn') or self._thread_local_connector.conn.closed:
            self._thread_local_connector.conn = aiohttp.TCPConnector(**self.config.connector_config)
            logger.debug(f"Created new TCPConnector for thread {threading.current_thread().name}")
        return self._thread_local_connector.conn
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create optimized aiohttp session"""
        connector = self.get_connector()
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=self.config.timeout_config,
            headers=self.config.headers,
            read_bufsize=self.config.read_buffer_size,
            skip_auto_headers={"User-Agent"},
            connector_owner=False,
        )
    
    async def cleanup_connector(self):
        """Clean up thread-local connector"""
        if hasattr(self._thread_local_connector, 'conn') and not self._thread_local_connector.conn.closed:
            await self._thread_local_connector.conn.close()
            logger.debug(f"Closed TCPConnector for thread {threading.current_thread().name}")

class CacheManager:
    """Manages various caches used by the search engine"""
    
    def __init__(self, max_cache_size: int = 500):
        self.max_cache_size = max_cache_size
        self._content_cache: Dict[str, str] = {}
        self._url_cache: Dict[str, bool] = {}
        self._failed_urls: Set[str] = set()
    
    @lru_cache(maxsize=2000)
    def is_valid_url_cached(self, url: str) -> bool:
        """Cached URL validation"""
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
    
    def get_content(self, url: str) -> Optional[str]:
        """Get cached content"""
        return self._content_cache.get(url)
    
    def set_content(self, url: str, content: str):
        """Cache content with size management"""
        if len(self._content_cache) > self.max_cache_size:
            old_keys = list(self._content_cache.keys())[:100]
            for key in old_keys:
                del self._content_cache[key]
        
        self._content_cache[url] = content
    
    def is_failed_url(self, url: str) -> bool:
        """Check if URL is in failed set"""
        return url in self._failed_urls
    
    def add_failed_url(self, url: str):
        """Add URL to failed set"""
        self._failed_urls.add(url)
    
    def clear_all(self):
        """Clear all caches"""
        self._content_cache.clear()
        self._failed_urls.clear()
        self._url_cache.clear()
        self.is_valid_url_cached.cache_clear()

class DuckSearch:
    """Main search class with multiple backend support"""
    
    def __init__(self):
        self.config = SearchConfig()
        self.session_manager = SessionManager(self.config)
        self.content_extractor = ContentExtractor(self.config)
        self.cache_manager = CacheManager()
        self.serper_engine = SerperSearchEngine()
        
        # Initialize DuckDuckGo engines
        self.search_engine = DuckDuckGoSearchResults(
            backend="text", output_format="list"
        )
        self.news_engine = DuckDuckGoSearchResults(
            backend="news", output_format="list", num_results=8
        )
        
        # Thread management
        self._warmup_done = False
        self._background_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="bg-duck"
        )
        self._sync_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="sync-async-bridge"
        )
        
        self._start_background_warmup()

    def _start_background_warmup(self):
        """Start background warmup task"""
        def warmup_task_wrapper():
            try:
                asyncio.run(self._warmup_sessions())
            except Exception as e:
                logger.debug(f"Warmup task error: {e}")
            finally:
                asyncio.run(self.session_manager.cleanup_connector())
        
        self._background_executor.submit(warmup_task_wrapper)

    async def _warmup_sessions(self):
        """Warm up connections"""
        session = None
        try:
            session = await self.session_manager.create_session()
            
            dummy_urls = ["http://example.com", "http://google.com"]
            for url in dummy_urls:
                try:
                    async with session.get(url, timeout=0.5) as resp:
                        await resp.read()
                        logger.debug(f"Warmup successful for {url} with status {resp.status}")
                except Exception as e:
                    logger.debug(f"Warmup failed for {url}: {e}")

            self._warmup_done = True
            logger.debug(f"Warmed up connections in background thread {threading.current_thread().name}")
        finally:
            if session and not session.closed:
                await session.close()
                logger.debug(f"Closed warmup ClientSession")

    async def _extract_content_blazing(self, session: aiohttp.ClientSession, url: str, limit: int = 300) -> str:
        """Extract content with caching"""
        if not url or self.cache_manager.is_failed_url(url):
            return ""
        
        cached_content = self.cache_manager.get_content(url)
        if cached_content is not None:
            return cached_content
            
        if not self.cache_manager.is_valid_url_cached(url):
            self.cache_manager.add_failed_url(url)
            return ""
        
        content = await self.content_extractor.extract_content(session, url, limit)
        
        if not content:
            self.cache_manager.add_failed_url(url)
            return ""
        
        self.cache_manager.set_content(url, content)
        return content

    async def _process_result_blazing(self, session: aiohttp.ClientSession, result: Dict) -> Dict:
        """Process a single search result"""
        url = result.get("link")
        if not url or self.cache_manager.is_failed_url(url):
            result["full_content"] = ""
            return result
            
        content = await self._extract_content_blazing(session, url)
        result["full_content"] = content
        return result

    async def _deep_search_blazing(self, results: List[Dict], k: int) -> List[Dict]:
        """Perform deep search with content extraction"""
        session = None
        try:
            session = await self.session_manager.create_session()
            
            if not results:
                return []
            
            max_concurrent = min(k * 8, 200)
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(result_item):
                async with semaphore:
                    return await self._process_result_blazing(session, result_item)
            
            tasks = []
            initial_results_copy = results[:k]
            
            for result in initial_results_copy:
                url = result.get("link", "")
                if url and not self.cache_manager.is_failed_url(url) and self.cache_manager.is_valid_url_cached(url):
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
            logger.debug(f"Deep search completed in {processing_time:.3f}s for {len(completed_results)} results")
            
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
            logger.debug("Deep search timeout - returning partial results")
            return self._handle_timeout_results(tasks, initial_results_copy, k)
        except Exception as e:
            logger.error(f"Unexpected error in deep search: {e}")
            for result in initial_results_copy:
                result["full_content"] = ""
            return initial_results_copy[:k]
        finally:
            if session and not session.closed:
                await session.close()
            await self.session_manager.cleanup_connector()

    def _handle_timeout_results(self, tasks: List, initial_results_copy: List[Dict], k: int) -> List[Dict]:
        """Handle timeout scenario and return partial results"""
        cancelled_count = 0
        for task in tasks:
            if not task.done():
                task.cancel()
                cancelled_count += 1
        
        logger.debug(f"Cancelled {cancelled_count} tasks due to timeout")
        
        partial_results = []
        for i, task in enumerate(tasks):
            original_result = initial_results_copy[i]
            if task.done():
                try:
                    result = task.result()
                    if isinstance(result, Exception):
                        original_result["full_content"] = ""
                    else:
                        partial_results.append(result)
                        continue
                except:
                    original_result["full_content"] = ""
            else:
                original_result["full_content"] = ""
            partial_results.append(original_result)
        
        return partial_results[:k]

    async def _search_with_serper(self, query: str, k: int = 6) -> List[Dict]:
        """Search using SERPER API with proper session management"""
        session = None
        try:
            # Create a new session with longer timeout for SERPER API
            connector = self.session_manager.get_connector()
            serper_timeout = aiohttp.ClientTimeout(total=15, connect=5)
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=serper_timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SerperBot/1.0)",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                },
                connector_owner=False,
            )
            
            results = await self.serper_engine.search(session, query, k)
            logger.info(f"SERPER API returned {len(results)} results for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"SERPER search failed: {e}")
            return []
        finally:
            if session and not session.closed:
                await session.close()

    def _determine_backend(self, backend: SearchBackend) -> SearchBackend:
        """Determine which backend to use"""
        if backend == "auto":
            return "serper" if self.serper_engine.is_available() else "duckduckgo"
        elif backend == "serper" and not self.serper_engine.is_available():
            logger.warning("SERPER API key not available, falling back to DuckDuckGo")
            return "duckduckgo"
        return backend

    def search_result(
        self, 
        query: str, 
        k: int = 6, 
        backend: SearchBackend = "auto", 
        deep_search: bool = True
    ) -> List[Dict]:
        """Main search method with multiple backend support"""
        start_time = time.time()
        actual_backend = self._determine_backend(backend)
        logger.info(f"Starting search for query: '{query}' using {actual_backend} backend")
        
        try:
            if actual_backend == "serper":
                # Use SERPER API
                def _run_serper_search():
                    return asyncio.run(self._search_with_serper(query, k))
                
                future = self._sync_executor.submit(_run_serper_search)
                results = future.result(timeout=2.5)
            else:
                # Use DuckDuckGo
                results = self.search_engine.invoke(query, max_results=max(k, 4))
                logger.info(f"DuckDuckGo returned {len(results)} results")
            
            if not results:
                logger.info(f"No initial results found for query: '{query}'")
                return []
                
        except Exception as e:
            logger.error(f"Search invocation error with {actual_backend}: {e}")
            return []
        
        if not deep_search:
            search_time = time.time() - start_time
            logger.info(f"⚡ Basic search complete: {search_time:.3f}s")
            return results[:k]
        
        logger.info(f"Initiating deep processing for {len(results)} initial results...")
        
        try:
            def _run_deep_search_wrapper():
                return asyncio.run(self._deep_search_blazing(results, k))

            future = self._sync_executor.submit(_run_deep_search_wrapper)
            final_results = future.result(timeout=2.5)

            search_time = time.time() - start_time
            logger.info(f"🚀 Deep search complete: {search_time:.3f}s using {actual_backend}")
            return final_results
                
        except concurrent.futures.TimeoutError:
            logger.error(f"Deep search timed out for query: '{query}'. Returning partial results.")
            for res in results[:k]:
                if "full_content" not in res:
                    res["full_content"] = ""
            return results[:k]
        except Exception as e:
            logger.error(f"Deep search error for query '{query}': {e}. Returning initial results.")
            for res in results[:k]:
                res["full_content"] = ""
            return results[:k]

    def today_new(self, category: str, backend: SearchBackend = "auto") -> List[Dict]:
        """Get news with backend selection support"""
        category_queries = {
            "technology": "latest tech science AI news",
            "finance": "latest finance market news", 
            "entertainment": "latest entertainment culture news",
            "sports": "latest sports news",
            "world": "latest world breaking news",
            "health": "latest health medical news"
        }
        
        query = category_queries.get(category, "latest breaking news")
        actual_backend = self._determine_backend(backend)
        
        try:
            if actual_backend == "serper":
                def _run_serper_news():
                    return asyncio.run(self._search_serper_news(query))
                
                future = self._sync_executor.submit(_run_serper_news)
                return future.result(timeout=2.0)
            else:
                return self.news_engine.invoke(query)
        except Exception as e:
            logger.error(f"News search error for category '{category}' with {actual_backend}: {e}")
            return []

    async def _search_serper_news(self, query: str) -> List[Dict]:
        """Search news using SERPER API with proper session management"""
        session = None
        try:
            # Create a new session with longer timeout for SERPER API
            connector = self.session_manager.get_connector()
            serper_timeout = aiohttp.ClientTimeout(total=15, connect=5)
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=serper_timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SerperBot/1.0)",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                },
                connector_owner=False,
            )
            
            return await self.serper_engine.search(session, query, 8, "news")
        finally:
            if session and not session.closed:
                await session.close()

    def clear_cache(self):
        """Clear all caches"""
        logger.info("Clearing all internal caches")
        self.cache_manager.clear_all()
        gc.collect()

    async def cleanup(self):
        """Cleanup all resources"""
        logger.info("Starting DuckSearch cleanup...")
        
        self.clear_cache()
        
        if self._background_executor:
            self._background_executor.shutdown(wait=True, cancel_futures=True)
            logger.debug("Background executor shutdown complete")
        if self._sync_executor:
            self._sync_executor.shutdown(wait=True, cancel_futures=True)
            logger.debug("Sync executor shutdown complete")
        
        logger.info("DuckSearch cleanup complete")

    def __del__(self):
        """Cleanup on object deletion"""
        try:
            if hasattr(self, '_background_executor') and self._background_executor:
                self._background_executor.shutdown(wait=False)
            if hasattr(self, '_sync_executor') and self._sync_executor:
                self._sync_executor.shutdown(wait=False)
        except Exception as e:
            logger.debug(f"Error during __del__ cleanup: {e}")