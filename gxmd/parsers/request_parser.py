import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable
from urllib.parse import urlparse

import aiohttp
import cloudscraper
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from selectolax.parser import HTMLParser, Node

from gxmd.abstracts.manga_parser import IMangaParser
from gxmd.config import USER_AGENT, PARSE_MANGA_INFO_TEMPLATE, registry, PARSE_CHAPTER_IMAGES_TEMPLATE
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.services.llm import llm, DEFAULT_SYSTEM_MESSAGE


class RequestParser(IMangaParser):
    soup: Node = None
    cookies = {}  # Per-domain cookies
    _session_pool: dict[str, aiohttp.ClientSession] = {}

    def __init__(self, manga_url: str, timeout=10):
        self.scraper_func = None
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=2)  # Minimal threads
        self.manga_url = manga_url

    async def close(self):
        """Close all sessions on shutdown"""
        for session in self._session_pool.values():
            await session.close()
        self._session_pool.clear()

    async def parse_manga_info(self):
        await self._load_page(self.manga_url)
        scraper_func = await self._get_scraper_func('manga_info')
        res: dict = scraper_func(self.soup)
        return res.get('manga_name'), [MangaChapter(**chapter) for chapter in res.get('manga_chapters')]

    async def parse_chapter_images(self, link: str) -> list[str]:
        """
        Parse chapter images

        Args:
            link (str): link to the chapter

        Returns:
            list[str]: A list of image links.
        """
        await self._load_page(link)
        self.scraper_func = self.scraper_func or await self._get_scraper_func('chapter_images')
        res: list[str] = self.scraper_func(self.soup)
        return res

    async def _load_page(self, url: str):
        """cloudscraper → steal cookies → aiohttp"""
        domain = urlparse(url).netloc

        if domain not in self._session_pool:
            # Bypass once per domain (sync, but rare)
            loop = asyncio.get_event_loop()
            scraper = cloudscraper.create_scraper()
            resp = await loop.run_in_executor(
                self.executor, partial(scraper.get, url, timeout=self.timeout)
            )
            cookies = {k: v for k, v in resp.cookies.items()}

            connector = aiohttp.TCPConnector(limit_per_host=20, ttl_dns_cache=300)
            self._session_pool[domain] = aiohttp.ClientSession(
                connector=connector,
                cookies=cookies,
                headers={'User-Agent': USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

            content = resp.text
        else:
            session = self._session_pool[domain]
            async with session.get(url) as resp:
                resp.raise_for_status()
                content = await resp.text()

        tree = HTMLParser(content)
        self.soup: Node = self.find_content(tree)  # Find FIRST
        self.clean_html(tree)  # Clean AFTER

    async def _get_scraper_func(self, purpose: str) -> Callable:
        domain = urlparse(self.manga_url).netloc
        scraper_file = registry.get_scraper_file(domain, purpose)

        if scraper_file.exists():
            code = scraper_file.read_text()
        else:
            template = PARSE_MANGA_INFO_TEMPLATE if purpose == 'manga_info' else PARSE_CHAPTER_IMAGES_TEMPLATE
            with (open(template, 'r') as f):
                messages = [DEFAULT_SYSTEM_MESSAGE,
                            HumanMessage(f.read().replace("{html}", "".join(self.soup.html.split())))]

                chain = llm | StrOutputParser()
                code: str = await chain.ainvoke(messages)
                code = code.strip().lstrip('```python').rstrip('```').strip()

                if code.lower() == "no":
                    raise Exception("website not supported")

        # Safely compile and return callable
        func = compile(code, '<scraper>', 'exec')
        local_ns = {
            "node": HTMLParser
        }
        exec(func, globals(), local_ns)
        registry.set_scraper_file(scraper_file, code)
        function_name = f"parse_{purpose}"
        return local_ns.get(function_name)

    @staticmethod
    def clean_html(tree: HTMLParser):
        """Conservative cleaning - only obvious noise."""
        selectors = [
            "nav", "footer", "aside", "script", "style", "noscript",
            "[class*='advert']", "[class^='ad-']",
            ".sp-wrapper", "[class*='sandpack']"
        ]
        # Clean AFTER finding content to avoid breaking structure
        for sel in selectors:
            for node in tree.css(sel):
                node.decompose()

    @staticmethod
    def find_content(tree: HTMLParser) -> Node:
        """Generic main content detection - multiple fallbacks."""
        selectors = [
            "main", "article", "[role='main']",
            ".content", "#content", ".main-content",
            ".entry-content",
            ".markdown-body", ".prose", ".mdx-content",
            "div[data-page]"
        ]
        for sel in selectors:
            if node := tree.css_first(sel):
                return node
        best_score = 0
        best_node = tree.body

        for div in tree.css("div"):
            text_len = len(div.text(strip=True))
            child_count = len(div.css("li, a"))  # Chapters have many links
            # Score: text + 100 per chapter-like child
            score = text_len + (child_count * 100)
            if score > best_score and text_len > 200:
                best_score = score
                best_node = div
        return best_node
