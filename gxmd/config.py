import os
from pathlib import Path

### Constants ###

USER_AGENT = 'Mozilla/5.0'
BASE_DIR = Path(__file__).parent
PARSE_MANGA_INFO_TEMPLATE = BASE_DIR / 'templates' / 'parse_manga_info_template'
PARSE_CHAPTER_IMAGES_TEMPLATE = BASE_DIR / 'templates' / 'parse_chapter_images_template'
SCRPERS_DIR = "~/.config/gxmd/scrapers"


class CodeRegistry:
    def __init__(self):
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


registry = CodeRegistry()
