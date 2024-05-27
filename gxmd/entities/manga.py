from dataclasses import dataclass
from gxmd.entities.manga_chapter import MangaChapter


@dataclass
class Manga:
    title: str
    url: str
    chapters: list[MangaChapter]
