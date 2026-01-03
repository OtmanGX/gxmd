import os
import re
from pathlib import Path

### Constants ###

USER_AGENT = 'Mozilla/5.0'
IMG_SRC_ATTR = 'data-src'
_RE_COMBINE_WHITESPACE = re.compile(r"\s+")
PARSE_MANGA_INFO_TEMPLATE = 'templates/parse_manga_info_template'
PARSE_CHAPTER_IMAGES_TEMPLATE = 'templates/parse_chapter_images_template'
SCRPERS_DIR = "~/.config/gxmd/scrapers"


class CodeRegistry:
    def __init__(self):
        # Base hardcoded defaults
        self._docs = {
            "langchain": "https://docs.langchain.com",
            "llama-index": "https://docs.llamaindex.ai",
            "openai": "https://platform.openai.com/docs",
        }
        self.scrapers_dir = Path(os.path.expanduser(SCRPERS_DIR))
        self.scrapers_dir.mkdir(exist_ok=True, parents=True)

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

    def register(self, name: str, url: str):
        self._docs[name.lower()] = url

    def list_supported(self):
        return list(self._docs.keys())


registry = CodeRegistry()
