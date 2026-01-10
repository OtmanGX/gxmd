from pathlib import Path

### Constants ###

USER_AGENT = 'Mozilla/5.0'
BASE_DIR = Path(__file__).parent
PARSE_MANGA_INFO_TEMPLATE = BASE_DIR / 'templates' / 'parse_manga_info_template'
PARSE_CHAPTER_IMAGES_TEMPLATE = BASE_DIR / 'templates' / 'parse_chapter_images_template'
SCRPERS_DIR = "~/.config/gxmd/scrapers"
MAX_TABS = 10
