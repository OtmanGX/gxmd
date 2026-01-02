import asyncio
from functools import partial
from urllib.parse import urlparse

import aiohttp
import cloudscraper

from gxmd.abstracts.fetch_strategy import FetchStrategy
from gxmd.config import USER_AGENT


class HttpClientStrategy(FetchStrategy):
    """Handles both standard aiohttp and cloudscraper-bypassed sessions."""
    def __init__(self, executor):
        self.executor = executor
        self.sessions: dict[str, aiohttp.ClientSession] = {}

    async def fetch(self, url: str) -> str:
        domain = urlparse(url).netloc

        if domain not in self.sessions:
            loop = asyncio.get_event_loop()
            scraper = cloudscraper.create_scraper()
            resp = await loop.run_in_executor(
                self.executor, partial(scraper.get, url, timeout=10)
            )
            cookies = {k: v for k, v in resp.cookies.items()}

            connector = aiohttp.TCPConnector(limit_per_host=20, ttl_dns_cache=300)
            self.sessions[domain] = aiohttp.ClientSession(
                connector=connector,
                cookies=cookies,
                headers={'User-Agent': USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=10)
            )
            return resp.text

        async with self.sessions[domain].get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def close(self):
        for session in self.sessions.values():
            await session.close()
