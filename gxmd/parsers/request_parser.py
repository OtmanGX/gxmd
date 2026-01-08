import posixpath
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from urllib.parse import urlparse, urljoin

from selectolax.parser import HTMLParser, Node

from gxmd.abstracts.manga_parser import IMangaParser
from gxmd.config import registry
from gxmd.entities.manga_chapter import MangaChapter
from gxmd.exceptions import GXMDownloaderError
from gxmd.parsers.strategies.http_strategy import HttpClientStrategy
from gxmd.parsers.strategies.playwright_strategy import PlaywrightStrategy
from gxmd.services.code_generator import code_generator
from gxmd.utils import minify_html, find_and_clean_content


class RequestParser(IMangaParser):
    _executor = ThreadPoolExecutor(max_workers=4)  # Minimal threads
    _manga_scraper: dict[str, Callable] = {}  # Per-domain
    _manga_chapter_scraper: dict[str, Callable] = {}  # Per-domain
    http_fetcher = HttpClientStrategy(_executor)
    render_fetcher = PlaywrightStrategy()

    async def parse_manga_info(self, manga_url: str):
        parsed_url = urlparse(manga_url)
        domain = parsed_url.netloc
        _, needs_render = registry.get_scraper_file(domain, 'manga_info')

        soup, render = await self._load_page(manga_url, render=True)
        scraper_func = await self._get_scraper_func(manga_url, soup, 'manga_info', render)
        res: dict = scraper_func(soup)
        manga_name = res.get('manga_name')
        manga_chapters = [MangaChapter(**chapter) for chapter in res.get('manga_chapters')]
        for chapter in manga_chapters:
            if not (chapter.link.startswith('http') or chapter.link.startswith('ftp')):
                if chapter.link.strip().startswith("/"):
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    chapter.link = urljoin(base_url, chapter.link)
                else:
                    base_url = posixpath.dirname(parsed_url.geturl())
                    chapter.link = posixpath.join(base_url, chapter.link)

        return manga_name, manga_chapters

    async def parse_chapter_images(self, chapter_link: str) -> list[str]:
        """
        Parse chapter images

        Args:
            chapter_link (str): link to the chapter

        Returns:
            list[str]: A list of image links.
        """
        domain = urlparse(chapter_link).netloc
        _, needs_render = registry.get_scraper_file(domain, 'chapter_images')

        soup, render = await self._load_page(chapter_link, True, render=True)
        scraper_func = await self._get_scraper_func(chapter_link, soup, 'chapter_images', render)
        res: list[str] = scraper_func(soup)
        return res

    async def _load_page(self, url: str, to_parse_images=False, render=True):
        """cloudscraper → steal cookies → aiohttp"""
        fetcher = self.render_fetcher if render else self.http_fetcher
        content = await fetcher.fetch(url)

        tree = HTMLParser(content)
        soup = find_and_clean_content(tree, to_parse_images)

        # Auto-fallback logic
        is_supported: bool = True if to_parse_images else len(soup.text(True, "", True)) > 150
        if not is_supported:
            if not render:
                print('Website needs rendering, switching strategy...')
                return await self._load_page(url, to_parse_images, render=True)
            else:
                raise GXMDownloaderError("Website not supported")

        return soup, render

    @classmethod
    async def _get_scraper_func(cls, url: str, soup: Node, purpose: str,
                                current_render_state: bool = False) -> Callable:
        domain = urlparse(url).netloc
        if purpose == "manga_info":
            if domain in cls._manga_scraper:
                return cls._manga_scraper.get(domain)
        else:
            if domain in cls._manga_chapter_scraper:
                return cls._manga_chapter_scraper.get(domain)

        scraper_file, _ = registry.get_scraper_file(domain, purpose)
        if scraper_file.exists():
            code = scraper_file.read_text()
        else:
            html_minified = minify_html(soup.html)
            code = code_generator.generate_manga_code(purpose, html_minified, url)

            if code.lower() == "no":
                raise Exception("website not supported")

        # Safely compile and return callable
        func = compile(code, '<scraper>', 'exec')
        local_ns = {
            "node": HTMLParser
        }
        exec(func, globals(), local_ns)
        registry.set_scraper_file(scraper_file, code, render=current_render_state)
        function_name = f"parse_{purpose}"
        scraper_func = local_ns.get(function_name)
        if purpose == "manga_info":
            cls._manga_scraper[domain] = scraper_func
        else:
            cls._manga_chapter_scraper[domain] = scraper_func
        return scraper_func

    @classmethod
    async def close(cls):
        """Close all sessions on shutdown"""
        await cls.http_fetcher.close()
        await cls.render_fetcher.close()
        cls._executor.shutdown(wait=True)

