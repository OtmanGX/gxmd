import os
from pathlib import Path
from typing import Callable

from gxmd.config import SCRPERS_DIR


class CodeRegistry:
    def __init__(self):
        self.scrapers_dir = Path(os.path.expanduser(SCRPERS_DIR))
        self.scrapers_dir.mkdir(exist_ok=True, parents=True)
        self._manga_scraper: dict[str, Callable] = {}  # Per-domain
        self._manga_chapter_scraper: dict[str, Callable] = {}  # Per-domain

    def get_scraper_func(self, purpose: str, domain: str) -> Callable | None:
        if purpose == "manga_info":
            if domain in self._manga_scraper:
                return self._manga_scraper.get(domain)
        else:
            if domain in self._manga_chapter_scraper:
                return self._manga_chapter_scraper.get(domain)

        return None

    def set_scraper_func(self, domain: str, purpose: str, scraper_func: Callable | None) -> None:
        if purpose == "manga_info":
            self._manga_scraper[domain] = scraper_func
        else:
            self._manga_chapter_scraper[domain] = scraper_func

    def get_scraper_file(self, domain: str, purpose: str = 'manga_info'):
        path = self.scrapers_dir / f"{domain}/{purpose}.py"
        render_flag = self.scrapers_dir / f"{domain}/{purpose}.render"
        return path, render_flag.exists()

    def set_scraper_file(self, path: Path, code: str, render=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding='utf-8')

        render_flag = path.with_suffix('.render')
        if render:
            render_flag.touch()
        else:
            render_flag.unlink(missing_ok=True)

# Global instance
registry = CodeRegistry()
