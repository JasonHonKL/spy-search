import asyncio
import aiohttp
import aiopg
import json
import os
import time
import logging
from datetime import datetime, timedelta
from html import unescape
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from selectolax.parser import HTMLParser
import re
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

class DuckSearch:
    def __init__(self):
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
            'database': os.getenv('POSTGRES_DB', 'search_cache'),
            'minsize': 5,
            'maxsize': 15,
        }
        
        # Connection pools
        self._db_pool = None
        self._http_session = None
        self._pool_lock = asyncio.Lock()
        
        # Timeouts
        self.fast_timeout = 1.0  # Reduced for faster response
        self.background_timeout = 8.0
        self.api_timeout = 2.0  # Specific timeout for API calls
        
        # HTTP configuration - optimized for speed
        self._http_config = {
            'connector': aiohttp.TCPConnector(
                limit=50,
                limit_per_host=20,
                ttl_dns_cache=600,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                force_close=False,
                resolver=aiohttp.resolver.AsyncResolver()
            ),
            'timeout': aiohttp.ClientTimeout(
                total=self.api_timeout,
                connect=0.5,
                sock_read=1.0
            ),
            'headers': {
                'User-Agent': 'Mozilla/5.0 (compatible; FastSearchBot/2.0)',
                'Accept': 'application/json,text/html,application/xhtml+xml',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        }
        
        # Caching
        self._url_cache = {}
        self._search_cache = {}  # Additional memory cache for searches
        self._cache_max_size = 2000
        self._failed_urls = set()
        self._background_tasks = set()
        
        # Performance tracking
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': 0,
            'content_extractions': 0
        }

    async def _get_http_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling."""
        if self._http_session is None or self._http_session.closed:
            async with self._pool_lock:
                if self._http_session is None or self._http_session.closed:
                    self._http_session = aiohttp.ClientSession(**self._http_config)
        return self._http_session

    async def _get_db_pool(self):
        """Get database connection pool with improved error handling."""
        if self._db_pool is None:
            async with self._pool_lock:
                if self._db_pool is None:
                    try:
                        self._db_pool = await aiopg.create_pool(**self.db_config)
                        await self._init_db()
                    except Exception as e:
                        logger.error(f"Failed to create DB pool: {e}")
                        # Continue without DB caching
                        return None
        return self._db_pool

    async def _init_db(self):
        """Initialize database tables with optimized schema."""
        if not self._db_pool:
            return
            
        try:
            async with self._db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Optimized search cache table
                    await cur.execute("""
                        CREATE TABLE IF NOT EXISTS search_cache (
                            query_hash TEXT PRIMARY KEY,
                            query TEXT NOT NULL,
                            results JSONB NOT NULL,
                            has_content BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Optimized URL content cache
                    await cur.execute("""
                        CREATE TABLE IF NOT EXISTS url_cache (
                            url_hash TEXT PRIMARY KEY,
                            url TEXT NOT NULL,
                            content TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Optimized indexes
                    await cur.execute("CREATE INDEX IF NOT EXISTS idx_search_created ON search_cache(created_at)")
                    await cur.execute("CREATE INDEX IF NOT EXISTS idx_url_created ON url_cache(created_at)")
                    await cur.execute("CREATE INDEX IF NOT EXISTS idx_search_has_content ON search_cache(has_content)")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def _hash_query(self, query: str) -> str:
        """Generate consistent hash for caching."""
        return hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL caching."""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _manage_memory_cache(self):
        """Efficient cache management."""
        if len(self._url_cache) > self._cache_max_size:
            # Remove oldest 25% of entries
            to_remove = len(self._url_cache) - int(self._cache_max_size * 0.75)
            keys_to_remove = list(self._url_cache.keys())[:to_remove]
            for key in keys_to_remove:
                self._url_cache.pop(key, None)
        
        if len(self._search_cache) > 500:
            # Keep search cache smaller
            to_remove = len(self._search_cache) - 375
            keys_to_remove = list(self._search_cache.keys())[:to_remove]
            for key in keys_to_remove:
                self._search_cache.pop(key, None)

    async def _get_cached_search(self, query: str) -> Optional[Tuple[List[Dict], bool]]:
        """Fast search cache retrieval with memory + DB fallback."""
        query_hash = self._hash_query(query)
        
        # Check memory cache first
        if query_hash in self._search_cache:
            cache_entry = self._search_cache[query_hash]
            if cache_entry['timestamp'] > time.time() - 3600:  # 1 hour
                self._stats['cache_hits'] += 1
                return cache_entry['results'], cache_entry['has_content']
        
        # Check database cache
        db_pool = await self._get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        SELECT results, has_content FROM search_cache 
                        WHERE query_hash = %s AND created_at > %s
                    """, (query_hash, datetime.now() - timedelta(hours=6)))
                    
                    row = await cur.fetchone()
                    if row:
                        results = json.loads(row[0])
                        has_content = row[1]
                        
                        # Update memory cache
                        self._search_cache[query_hash] = {
                            'results': results,
                            'has_content': has_content,
                            'timestamp': time.time()
                        }
                        self._stats['cache_hits'] += 1
                        return results, has_content
        except Exception as e:
            logger.debug(f"DB cache retrieval failed: {e}")
        
        self._stats['cache_misses'] += 1
        return None

    async def _cache_search_results(self, query: str, results: List[Dict], has_content: bool = False):
        """Fast search result caching."""
        query_hash = self._hash_query(query)
        
        # Update memory cache immediately
        self._search_cache[query_hash] = {
            'results': results,
            'has_content': has_content,
            'timestamp': time.time()
        }
        
        # Update DB cache asynchronously
        db_pool = await self._get_db_pool()
        if db_pool:
            try:
                async with db_pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            INSERT INTO search_cache (query_hash, query, results, has_content)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (query_hash) DO UPDATE SET
                                results = EXCLUDED.results,
                                has_content = EXCLUDED.has_content,
                                created_at = CURRENT_TIMESTAMP
                        """, (query_hash, query, json.dumps(results), has_content))
            except Exception as e:
                logger.debug(f"DB cache storage failed: {e}")

    async def _get_url_content(self, url: str) -> str:
        """Optimized URL content retrieval."""
        if not url or not self._is_valid_url(url) or url in self._failed_urls:
            return ""
        
        url_hash = self._hash_url(url)
        
        # Check memory cache
        if url_hash in self._url_cache:
            return self._url_cache[url_hash]
        
        # Check DB cache
        db_pool = await self._get_db_pool()
        if db_pool:
            try:
                async with db_pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("""
                            SELECT content FROM url_cache 
                            WHERE url_hash = %s AND created_at > %s
                        """, (url_hash, datetime.now() - timedelta(days=3)))
                        
                        row = await cur.fetchone()
                        if row and row[0]:
                            content = row[0]
                            self._url_cache[url_hash] = content
                            return content
            except Exception as e:
                logger.debug(f"URL cache retrieval failed: {e}")
        
        # Scrape content
        return await self._scrape_url_content(url, url_hash)

    async def _scrape_url_content(self, url: str, url_hash: str) -> str:
        """Fast URL content scraping with improved error handling."""
        try:
            session = await self._get_http_session()
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    self._failed_urls.add(url)
                    return ""
                
                # Read with size limit
                content_bytes = await response.content.read(30000)  # 30KB limit
                content_str = content_bytes.decode('utf-8', errors='ignore')
                
                text_content = self._extract_text_fast(content_str)
                
                if len(text_content) < 30:
                    self._failed_urls.add(url)
                    return ""
                
                # Cache content
                self._url_cache[url_hash] = text_content
                await self._cache_url_content(url, url_hash, text_content)
                self._stats['content_extractions'] += 1
                
                return text_content
                
        except Exception as e:
            logger.debug(f"URL scraping failed for {url}: {e}")
            self._failed_urls.add(url)
            return ""

    def _extract_text_fast(self, html: str) -> str:
        """Optimized text extraction."""
        try:
            tree = HTMLParser(html)
            
            # Fast content extraction - try most common patterns first
            for selector in ['article p', 'main p', '.content p', 'p']:
                elements = tree.css(selector)
                if len(elements) >= 2:
                    texts = []
                    for elem in elements[:8]:  # Limit processing
                        text = elem.text(strip=True)
                        if text and 20 < len(text) < 300:
                            texts.append(text)
                        if len(texts) >= 5:
                            break
                    
                    if len(texts) >= 2:
                        result = unescape(' '.join(texts))
                        return re.sub(r'\s+', ' ', result)[:600]
            
            # Fallback to divs
            divs = tree.css('div')[:10]
            texts = []
            for div in divs:
                text = div.text(strip=True)
                if text and 40 < len(text) < 400:
                    texts.append(text)
                if len(texts) >= 3:
                    break
            
            if texts:
                result = unescape(' '.join(texts))
                return re.sub(r'\s+', ' ', result)[:600]
                
        except Exception:
            pass
        
        return ""

    async def _cache_url_content(self, url: str, url_hash: str, content: str):
        """Async URL content caching."""
        db_pool = await self._get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO url_cache (url_hash, url, content)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (url_hash) DO UPDATE SET
                            content = EXCLUDED.content,
                            created_at = CURRENT_TIMESTAMP
                    """, (url_hash, url, content))
        except Exception as e:
            logger.debug(f"URL cache storage failed: {e}")

    @lru_cache(maxsize=2000)
    def _is_valid_url(self, url: str) -> bool:
        """Cached URL validation."""
        try:
            if not url or len(url) < 8:
                return False
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ('http', 'https'))
        except:
            return False

    async def _search_serper(self, query: str, num_results: int = 6) -> List[Dict]:
        """Optimized Serper API call with improved error handling."""
        payload = {"q": query, "num": num_results}
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            session = await self._get_http_session()
            async with session.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers
            ) as response:
                self._stats['api_calls'] += 1
                
                if response.status == 200:
                    data = await response.json()
                    return self._format_serper_results(data)
                else:
                    logger.error(f"Serper API error: {response.status}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.error("Serper API timeout")
            return []
        except Exception as e:
            logger.error(f"Serper API request failed: {e}")
            return []

    def _format_serper_results(self, data: dict) -> List[Dict]:
        """Fast result formatting."""
        return [
            {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', ''),
                'full_content': ''
            }
            for result in data.get('organic', [])
        ]

    async def _add_content_to_results(self, results: List[Dict]) -> List[Dict]:
        """Parallel content extraction with controlled concurrency."""
        if not results:
            return results
            
        semaphore = asyncio.Semaphore(15)  # Increased concurrency
        
        async def process_result(result):
            async with semaphore:
                url = result.get('link', '')
                if url:
                    content = await self._get_url_content(url)
                    result = result.copy()
                    result['full_content'] = content
                return result
        
        tasks = [process_result(result) for result in results]
        try:
            enhanced_results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in enhanced_results if not isinstance(r, Exception)]
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return results

    async def _background_content_extraction(self, results: List[Dict], query: str):
        """Optimized background content extraction."""
        try:
            logger.info(f"Starting background extraction for {len(results)} results")
            
            enhanced_results = await asyncio.wait_for(
                self._add_content_to_results(results),
                timeout=self.background_timeout
            )
            
            content_count = sum(1 for r in enhanced_results if r.get('full_content', '').strip())
            
            if content_count > 0:
                await self._cache_search_results(query, enhanced_results, has_content=True)
                logger.info(f"Background extraction completed: {content_count}/{len(enhanced_results)} with content")
            
        except Exception as e:
            logger.error(f"Background extraction failed: {e}")
        finally:
            current_task = asyncio.current_task()
            if current_task in self._background_tasks:
                self._background_tasks.remove(current_task)

    async def _async_search(self, query: str, k: int, deep_search: bool) -> List[Dict]:
        """Optimized main search implementation."""
        # Fast cache check
        cache_result = await self._get_cached_search(query)
        if cache_result:
            cached_results, has_content = cache_result
            logger.info(f"Cache hit: '{query}' (content: {has_content})")
            
            if has_content or not deep_search:
                return cached_results[:k]
            else:
                # Start background enhancement
                task = asyncio.create_task(
                    self._background_content_extraction(cached_results, query)
                )
                self._background_tasks.add(task)
                return cached_results[:k]
        
        # Fresh search
        logger.info(f"Fresh search: '{query}'")
        search_results = await self._search_serper(query, k)
        if not search_results:
            return []
        
        # Cache basic results immediately
        await self._cache_search_results(query, search_results, has_content=False)
        
        if not deep_search:
            return search_results
        
        # Fast content extraction attempt
        try:
            enhanced_results = await asyncio.wait_for(
                self._add_content_to_results(search_results),
                timeout=self.fast_timeout
            )
            
            content_count = sum(1 for r in enhanced_results if r.get('full_content', '').strip())
            
            if content_count > 0:
                await self._cache_search_results(query, enhanced_results, has_content=True)
                logger.info(f"Fast extraction: {content_count}/{len(enhanced_results)} with content")
                return enhanced_results
            
        except asyncio.TimeoutError:
            logger.info("Fast timeout - starting background processing")
        
        # Background processing fallback
        task = asyncio.create_task(
            self._background_content_extraction(search_results, query)
        )
        self._background_tasks.add(task)
        return search_results

    def search_result(self, query: str, k: int = 6, backend: str = "text", deep_search: bool = True) -> List[Dict]:
        """Main search function with performance optimization."""
        start_time = time.time()
        logger.info(f"Search: '{query}' (k={k}, deep={deep_search})")
        
        try:
            # Handle async execution more efficiently
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(self._async_search(query, k, deep_search))
                # Non-blocking wait
                while not task.done():
                    asyncio.sleep(0)
                results = task.result()
            except RuntimeError:
                results = asyncio.run(self._async_search(query, k, deep_search))
            
            elapsed = time.time() - start_time
            content_count = sum(1 for r in results if r.get('full_content', '').strip())
            
            logger.info(f"Search completed: {elapsed:.2f}s, {len(results)} results, {content_count} with content")
            logger.info(f"Stats - Cache hits: {self._stats['cache_hits']}, API calls: {self._stats['api_calls']}")
            
            # Manage cache size
            self._manage_memory_cache()
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []

    def today_new(self, category: str) -> List[Dict]:
        """Optimized news search."""
        category_queries = {
            "technology": "latest tech AI news today",
            "finance": "finance market news today",
            "entertainment": "entertainment news today",
            "sports": "sports news today",
            "world": "world news today",
            "health": "health news today"
        }
        
        query = category_queries.get(category, "breaking news today")
        
        async def _get_news():
            try:
                payload = {"q": query, "num": 8, "type": "news"}
                headers = {
                    'X-API-KEY': self.serper_api_key,
                    'Content-Type': 'application/json'
                }
                
                session = await self._get_http_session()
                async with session.post(
                    "https://google.serper.dev/news",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                'title': item.get('title', ''),
                                'link': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'date': item.get('date', ''),
                                'source': item.get('source', ''),
                                'full_content': ''
                            }
                            for item in data.get('news', [])
                        ]
                    return []
            except Exception as e:
                logger.error(f"News search failed: {e}")
                return []
        
        try:
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(_get_news())
                while not task.done():
                    asyncio.sleep(0)
                return task.result()
            except RuntimeError:
                return asyncio.run(_get_news())
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return []

    async def cleanup(self):
        """Clean up all resources."""
        # Cancel background tasks
        if self._background_tasks:
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            self._background_tasks.clear()
        
        # Close HTTP session
        if self._http_session and not self._http_session.closed:
            await self._http_session.close()
            self._http_session = None
        
        # Close DB pool
        if self._db_pool:
            self._db_pool.close()
            await self._db_pool.wait_closed()
            self._db_pool = None

    def clear_cache(self):
        """Clear all caches efficiently."""
        self._url_cache.clear()
        self._search_cache.clear()
        self._failed_urls.clear()
        self._is_valid_url.cache_clear()
        
        # Clear old DB entries
        async def _clear_db():
            db_pool = await self._get_db_pool()
            if not db_pool:
                return
                
            try:
                async with db_pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "DELETE FROM search_cache WHERE created_at < %s", 
                            (datetime.now() - timedelta(hours=12),)
                        )
                        await cur.execute(
                            "DELETE FROM url_cache WHERE created_at < %s",
                            (datetime.now() - timedelta(days=3),)
                        )
            except Exception as e:
                logger.error(f"DB cache clear failed: {e}")
        
        try:
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(_clear_db())
                while not task.done():
                    asyncio.sleep(0)
                task.result()
            except RuntimeError:
                asyncio.run(_clear_db())
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")

    def get_stats(self) -> Dict:
        """Get performance statistics."""
        return self._stats.copy()


# Global instance management - unchanged for compatibility
_search_instance = None

def get_search_instance():
    """Get shared search instance."""
    global _search_instance
    if _search_instance is None:
        _search_instance = DuckSearch()
    return _search_instance

def search_with_shared_instance(query: str, k: int = 6, backend: str = "text", deep_search: bool = True) -> List[Dict]:
    """Search using shared instance."""
    instance = get_search_instance()
    return instance.search_result(query, k, backend, deep_search)