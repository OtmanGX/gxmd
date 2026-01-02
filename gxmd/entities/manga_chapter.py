from dataclasses import dataclass


@dataclass(frozen=False)
class MangaChapter:
    """Represents a manga chapter"""
    name: str
    link: str
