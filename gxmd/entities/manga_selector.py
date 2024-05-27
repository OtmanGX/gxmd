from dataclasses import dataclass
from typing import Optional

from gxmd.constants import IMG_SRC_ATTR


@dataclass(frozen=True)
class MangaSelector:
    list_chapters: str
    chapter_images: str
    manga_name: Optional[str] = None
    chapter_link_attr: str = 'href'
    chapter_name_attr: Optional[str] = None
    image_link_attr: str = IMG_SRC_ATTR
    render: bool = False

